from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import current_user
from app.core.config import settings
from app.models import User
from app.schemas.auth import AppConfig
from app.schemas.place import GeoSuggestion
from app.services.geocode import GeocoderUnavailable, suggest

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/config", response_model=AppConfig)
def config() -> AppConfig:
    return AppConfig(
        geocoder_enabled=bool(settings.dadata_api_key),
        default_center=(settings.default_center_lat, settings.default_center_lon),
        default_city=settings.default_city,
        media_url=settings.media_url,
        max_upload_mb=settings.max_upload_mb,
    )


@router.get("/geo/suggest", response_model=list[GeoSuggestion])
async def geo_suggest(
    q: str = Query(min_length=3, max_length=200),
    city: str | None = None,
    user: User = Depends(current_user),
) -> list[GeoSuggestion]:
    try:
        return await suggest(q, city if city is not None else settings.default_city)
    except GeocoderUnavailable as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"Подсказки адресов недоступны: {exc}") from exc
