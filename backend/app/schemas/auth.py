from datetime import datetime

from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: int
    display_name: str
    accent: str

    model_config = {"from_attributes": True}


class UserMe(UserPublic):
    username: str
    created_at: datetime


USERNAME_PATTERN = r"^[A-Za-z0-9_.-]{3,32}$"


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=6, max_length=128)


class RegisterRequest(LoginRequest):
    invite_code: str = Field(min_length=4, max_length=32)
    display_name: str | None = Field(default=None, max_length=80)


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=80)
    accent: str | None = Field(default=None, max_length=16)


class InvitePublic(BaseModel):
    id: int
    code: str
    created_at: datetime
    expires_at: datetime | None
    used_at: datetime | None
    used_by: UserPublic | None

    model_config = {"from_attributes": True}


class AppConfig(BaseModel):
    geocoder_enabled: bool
    default_center: tuple[float, float]
    default_city: str
    media_url: str
    max_upload_mb: int
