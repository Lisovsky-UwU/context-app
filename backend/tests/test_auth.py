def test_register_requires_valid_invite(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "guest", "password": "parol123", "invite_code": "NOPE1234"},
    )
    assert response.status_code == 400
    assert "приглашения" in response.json()["detail"]


def test_invite_is_single_use(client, invite_code, user):
    response = client.post(
        "/api/auth/register",
        json={"username": "petya", "password": "parol123", "invite_code": invite_code},
    )
    assert response.status_code == 400


def test_login_logout_cycle(client, user):
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401

    assert client.post(
        "/api/auth/login", json={"username": "vera", "password": "wrong-pass"}
    ).status_code == 401

    response = client.post(
        "/api/auth/login", json={"username": "VERA", "password": "parol123"}
    )
    assert response.status_code == 200
    assert client.get("/api/auth/me").json()["username"] == "vera"


def test_username_is_taken_only_once(client, invite_code, user):
    second = client.post("/api/invites").json()["code"]
    response = client.post(
        "/api/auth/register",
        json={"username": "Vera", "password": "parol123", "invite_code": second},
    )
    assert response.status_code == 400
    assert "занято" in response.json()["detail"]


def test_display_name_defaults_to_login_and_can_be_set(client, invite_code, user):
    assert user["display_name"] == "vera"

    second = client.post("/api/invites").json()["code"]
    client.post("/api/auth/logout")
    registered = client.post(
        "/api/auth/register",
        json={
            "username": "petya",
            "password": "parol123",
            "invite_code": second,
            "display_name": "Петя",
        },
    ).json()
    assert registered["display_name"] == "Петя"
    assert registered["username"] == "petya"

    renamed = client.patch("/api/auth/me", json={"display_name": "Пётр"}).json()
    assert renamed["display_name"] == "Пётр"
    assert renamed["username"] == "petya"


def test_member_can_create_invite(client, user):
    response = client.post("/api/invites")
    assert response.status_code == 201
    assert len(response.json()["code"]) == 8
    assert client.get("/api/invites").json()[0]["used_at"] is None


def test_places_require_auth(client):
    assert client.get("/api/places").status_code == 401
