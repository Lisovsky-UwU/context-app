from datetime import date, timedelta

from tests.conftest import make_image_bytes


def create_place(client, title="Бар «Стрелка»", category="bar"):
    response = client.post(
        "/api/places",
        json={
            "title": title,
            "category": category,
            "description": "Говорят, лучший вид на реку",
            "address": "Москва, Берсеневская набережная, 14с5",
            "lat": 55.741,
            "lon": 37.608,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_place_travels_from_wish_to_visited(client, user):
    place = create_place(client)
    assert place["status"] == "wish"
    assert place["created_by"]["display_name"] == "vera"

    visit = client.post(
        "/api/visits",
        json={
            "place_id": place["id"],
            "scheduled_date": (date.today() + timedelta(days=3)).isoformat(),
            "scheduled_time": "19:30:00",
            "note": "Столик у окна",
        },
    ).json()
    assert visit["status"] == "planned"
    assert [p["display_name"] for p in visit["participants"]] == ["vera"]

    planned = client.get("/api/places", params={"status": "planned"}).json()
    assert [item["id"] for item in planned] == [place["id"]]
    assert planned[0]["next_visit"]["scheduled_time"] == "19:30:00"

    photos = client.post(
        f"/api/visits/{visit['id']}/photos",
        files=[("files", ("vid.jpg", make_image_bytes(), "image/jpeg"))],
        data={"caption": "Вид с террасы"},
    )
    assert photos.status_code == 201, photos.text
    assert photos.json()[0]["thumb_url"].endswith("_t.webp")

    client.patch(f"/api/visits/{visit['id']}", json={"status": "done"})

    detail = client.get(f"/api/places/{place['id']}").json()
    assert detail["status"] == "visited"
    assert detail["photo_count"] == 1
    assert detail["cover_url"] is not None
    assert detail["last_visit_date"] == visit["scheduled_date"]


def test_roulette_pool_skips_planned_and_visited(client, user):
    wish = create_place(client, "Музей света")
    planned = create_place(client, "Кофейня «Филин»", category="cafe")

    client.post(
        "/api/visits",
        json={
            "place_id": planned["id"],
            "scheduled_date": (date.today() + timedelta(days=1)).isoformat(),
        },
    )

    pool = client.get("/api/places/roulette-pool").json()
    assert [item["id"] for item in pool] == [wish["id"]]

    with_planned = client.get("/api/places/roulette-pool", params={"include_planned": True}).json()
    assert {item["id"] for item in with_planned} == {wish["id"], planned["id"]}

    empty = client.get("/api/places/roulette-pool", params={"category": "restaurant"}).json()
    assert empty == []


def test_interest_and_review(client, user):
    place = create_place(client)

    interested = client.put(f"/api/places/{place['id']}/interest").json()
    assert interested["interest_count"] == 1
    assert interested["interested"] is True
    assert client.put(f"/api/places/{place['id']}/interest").json()["interest_count"] == 1

    dropped = client.delete(f"/api/places/{place['id']}/interest").json()
    assert dropped["interest_count"] == 0

    reviewed = client.put(f"/api/places/{place['id']}/review", json={"score": 5, "text": "Вернёмся"}).json()
    assert reviewed["average_score"] == 5.0
    assert reviewed["my_review"]["text"] == "Вернёмся"

    updated = client.put(f"/api/places/{place['id']}/review", json={"score": 3, "text": "Шумно"}).json()
    assert updated["average_score"] == 3.0
    assert len(updated["reviews"]) == 1


def test_search_and_filters(client, user):
    create_place(client, "Бар «Стрелка»")
    create_place(client, "Кофейня «Филин»", category="cafe")

    assert len(client.get("/api/places", params={"q": "филин"}).json()) == 1
    assert len(client.get("/api/places", params={"category": "bar"}).json()) == 1
    assert len(client.get("/api/places", params={"q": "набережная"}).json()) == 2


def test_upload_rejects_non_image(client, user):
    place = create_place(client)
    visit = client.post(
        "/api/visits",
        json={"place_id": place["id"], "scheduled_date": date.today().isoformat()},
    ).json()

    response = client.post(
        f"/api/visits/{visit['id']}/photos",
        files=[("files", ("notes.txt", b"not an image at all", "text/plain"))],
    )
    assert response.status_code == 415
    assert "не похож на изображение" in response.json()["detail"]


def test_deleting_place_removes_photo_files(client, user):
    place = create_place(client)
    visit = client.post(
        "/api/visits",
        json={"place_id": place["id"], "scheduled_date": date.today().isoformat()},
    ).json()
    client.post(
        f"/api/visits/{visit['id']}/photos",
        files=[("files", ("vid.jpg", make_image_bytes(), "image/jpeg"))],
    )

    from app.core.config import settings

    stored = list((settings.upload_dir / str(place["id"])).glob("*.webp"))
    assert len(stored) == 2

    assert client.delete(f"/api/places/{place['id']}").status_code == 204
    assert list((settings.upload_dir / str(place["id"])).glob("*.webp")) == []
