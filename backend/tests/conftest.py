import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import DEFAULT_CATEGORIES, Category, Invite


@pytest.fixture
def client(tmp_path: Path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    @event.listens_for(engine, "connect")
    def _unicode_lower(dbapi_connection, _record):
        # Встроенный lower() в SQLite знает только латиницу, а ilike опирается на него
        dbapi_connection.create_function("lower", 1, lambda value: value.lower() if value else value)

    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    # В рабочей базе стартовый набор категорий заводит миграция.
    with TestSession() as db:
        db.add_all(
            Category(name=name, color=color, position=position)
            for position, (name, color) in enumerate(DEFAULT_CATEGORIES)
        )
        db.commit()

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    original_upload_dir = settings.upload_dir
    settings.upload_dir = tmp_path / "uploads"

    with TestClient(app) as test_client:
        test_client.session_factory = TestSession
        yield test_client

    app.dependency_overrides.clear()
    settings.upload_dir = original_upload_dir


@pytest.fixture
def invite_code(client) -> str:
    with client.session_factory() as db:
        invite = Invite(code="TESTCODE")
        db.add(invite)
        db.commit()
    return "TESTCODE"


@pytest.fixture
def user(client, invite_code):
    response = client.post(
        "/api/auth/register",
        json={"username": "vera", "password": "parol123", "invite_code": invite_code},
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def categories(client, user) -> dict[str, int]:
    return {item["name"]: item["id"] for item in client.get("/api/categories").json()}


def make_image_bytes(color: str = "purple") -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (900, 600), color).save(buffer, "JPEG")
    return buffer.getvalue()
