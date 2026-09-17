import httpx

from app.core.config import settings
from app.schemas.place import GeoSuggestion

SUGGEST_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"


class GeocoderUnavailable(Exception):
    pass


def _to_float(value: str | None) -> float | None:
    try:
        return float(value) if value else None
    except ValueError:
        return None


def _parse(payload: dict) -> list[GeoSuggestion]:
    suggestions: list[GeoSuggestion] = []
    for item in payload.get("suggestions") or []:
        data = item.get("data") or {}
        address = item.get("value") or ""
        suggestions.append(
            GeoSuggestion(
                title=address,
                address=data.get("unrestricted_value") or address,
                lat=_to_float(data.get("geo_lat")),
                lon=_to_float(data.get("geo_lon")),
            )
        )
    return suggestions


async def suggest(query: str, city: str | None = None) -> list[GeoSuggestion]:
    """Подсказки адресов через DaData. Ключ остаётся на сервере."""
    if not settings.dadata_api_key:
        raise GeocoderUnavailable("Ключ DaData не задан")

    body: dict = {"query": query, "count": 8}
    if city:
        body["locations"] = [{"city": city}]
        body["restrict_value"] = False

    headers = {
        "Authorization": f"Token {settings.dadata_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            response = await client.post(SUGGEST_URL, json=body, headers=headers)
    except httpx.HTTPError as exc:
        raise GeocoderUnavailable(str(exc)) from exc

    if response.status_code == 403:
        raise GeocoderUnavailable("DaData отклонила ключ")
    if response.status_code != 200:
        raise GeocoderUnavailable(f"DaData ответила {response.status_code}")
    return _parse(response.json())
