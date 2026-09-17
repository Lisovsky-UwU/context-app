from tests.test_flow import create_place


def test_default_set_is_available(client, user, categories):
    assert "Бар" in categories
    assert len(categories) == 7


def test_create_rename_and_recolor(client, user, categories):
    created = client.post("/api/categories", json={"name": "Театр", "color": "rose"})
    assert created.status_code == 201, created.text
    category = created.json()
    assert category["place_count"] == 0

    renamed = client.patch(
        f"/api/categories/{category['id']}", json={"name": "Театры", "color": "teal"}
    ).json()
    assert renamed["name"] == "Театры"
    assert renamed["color"] == "teal"


def test_name_and_color_are_checked(client, user, categories):
    duplicate = client.post("/api/categories", json={"name": "бар", "color": "mint"})
    assert duplicate.status_code == 400
    assert "уже есть" in duplicate.json()["detail"]

    wrong_color = client.post("/api/categories", json={"name": "Театр", "color": "ultramarine"})
    assert wrong_color.status_code == 400
    assert "палитре" in wrong_color.json()["detail"]


def test_place_keeps_category_after_rename(client, user, categories):
    place = create_place(client, category_id=categories["Бар"])
    client.patch(f"/api/categories/{categories['Бар']}", json={"name": "Бары и рюмочные"})

    assert client.get(f"/api/places/{place['id']}").json()["category"]["name"] == "Бары и рюмочные"


def test_busy_category_needs_a_target_to_move_places(client, user, categories):
    place = create_place(client, category_id=categories["Бар"])

    blocked = client.delete(f"/api/categories/{categories['Бар']}")
    assert blocked.status_code == 409
    assert "1 мест" in blocked.json()["detail"]

    moved = client.delete(
        f"/api/categories/{categories['Бар']}", params={"move_to": categories["Ресторан"]}
    )
    assert moved.status_code == 204
    assert client.get(f"/api/places/{place['id']}").json()["category"]["name"] == "Ресторан"


def test_places_can_be_left_without_category(client, user, categories):
    place = create_place(client, category_id=categories["Бар"])

    assert client.delete(
        f"/api/categories/{categories['Бар']}", params={"move_to": 0}
    ).status_code == 204

    detail = client.get(f"/api/places/{place['id']}").json()
    assert detail["category"] is None
    assert len(client.get("/api/categories").json()) == 6


def test_place_count_is_reported(client, user, categories):
    create_place(client, category_id=categories["Бар"])
    create_place(client, "Ещё бар", category_id=categories["Бар"])

    listed = {item["name"]: item["place_count"] for item in client.get("/api/categories").json()}
    assert listed["Бар"] == 2
    assert listed["Кофейня"] == 0


def test_unknown_category_is_rejected(client, user):
    response = client.post("/api/places", json={"title": "Место", "category_id": 999})
    assert response.status_code == 404
    assert "Категория" in response.json()["detail"]
