from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import Photo, User, Visit
from app.schemas.place import PhotoPublic
from app.services.media import UnsupportedImage, delete_image, save_image
from app.services.places import photo_public

router = APIRouter(tags=["photos"])


@router.post(
    "/visits/{visit_id}/photos",
    response_model=list[PhotoPublic],
    status_code=status.HTTP_201_CREATED,
)
async def upload_photos(
    visit_id: int,
    files: list[UploadFile] = File(...),
    caption: str = Form(default=""),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[PhotoPublic]:
    visit = db.get(Visit, visit_id)
    if visit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Поход не найден")

    limit = settings.max_upload_mb * 1024 * 1024
    created: list[Photo] = []
    for upload in files:
        raw = await upload.read()
        if len(raw) > limit:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"«{upload.filename}» больше {settings.max_upload_mb} МБ. Сожмите фото и попробуйте снова",
            )
        try:
            meta = save_image(raw, visit.place_id)
        except UnsupportedImage:
            raise HTTPException(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                f"«{upload.filename}» не похож на изображение",
            ) from None

        photo = Photo(
            visit_id=visit.id,
            place_id=visit.place_id,
            uploaded_by_id=user.id,
            caption=caption[:300],
            **meta,
        )
        db.add(photo)
        created.append(photo)

    db.commit()
    for photo in created:
        db.refresh(photo)
    return [photo_public(photo) for photo in created]


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> None:
    photo = db.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Фотография не найдена")
    delete_image(photo.filename, photo.thumb_filename)
    db.delete(photo)
    db.commit()
