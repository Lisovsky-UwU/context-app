import io
import uuid
from pathlib import Path

from PIL import Image, ImageOps

from app.core.config import settings

MAX_SIDE = 2000
THUMB_SIDE = 640
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}


class UnsupportedImage(Exception):
    pass


def media_url(filename: str | None) -> str | None:
    if not filename:
        return None
    return f"{settings.media_url.rstrip('/')}/{filename}"


def save_image(raw: bytes, place_id: int) -> dict:
    """Сохраняет снимок в webp: полноразмерную версию и превью. Возвращает метаданные."""
    try:
        image = Image.open(io.BytesIO(raw))
        image = ImageOps.exif_transpose(image)
        image.load()
    except Exception as exc:  # noqa: BLE001 — любой сбой декодирования трактуем одинаково
        raise UnsupportedImage(str(exc)) from exc

    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    full = image.copy()
    full.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    thumb = image.copy()
    thumb.thumbnail((THUMB_SIDE, THUMB_SIDE), Image.LANCZOS)

    place_dir = settings.upload_dir / str(place_id)
    place_dir.mkdir(parents=True, exist_ok=True)

    stem = uuid.uuid4().hex
    full_name = f"{stem}.webp"
    thumb_name = f"{stem}_t.webp"
    full.save(place_dir / full_name, "WEBP", quality=86, method=5)
    thumb.save(place_dir / thumb_name, "WEBP", quality=80, method=5)

    return {
        "filename": f"{place_id}/{full_name}",
        "thumb_filename": f"{place_id}/{thumb_name}",
        "width": full.width,
        "height": full.height,
    }


def delete_image(filename: str, thumb_filename: str) -> None:
    for name in (filename, thumb_filename):
        if not name:
            continue
        path: Path = settings.upload_dir / name
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
