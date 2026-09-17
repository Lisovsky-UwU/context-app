from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Context App"
    database_url: str = "postgresql+psycopg://context:context@localhost:5432/context"

    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_days: int = 30
    cookie_name: str = "context_session"
    cookie_secure: bool = True
    cookie_domain: str | None = None

    upload_dir: Path = Path("data/uploads")
    media_url: str = "/media"
    max_upload_mb: int = 15

    # DaData: ключ подсказок адресов, живёт только на сервере
    dadata_api_key: str = ""
    default_center_lat: float = 55.751244
    default_center_lon: float = 37.618423
    default_city: str = "Москва"

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
