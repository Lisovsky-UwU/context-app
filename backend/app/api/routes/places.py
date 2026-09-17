import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Category, Interest, Photo, Place, Review, User
from app.schemas.place import (
    PlaceDetail,
    PlaceInput,
    PlaceListItem,
    PlacePatch,
    ReviewInput,
)
from app.services import places as place_service
from app.services.media import delete_image

router = APIRouter(prefix="/places", tags=["places"])

SORTS = {
    "recent": lambda item: item.id * -1,
    "interest": lambda item: (-item.interest_count, -item.id),
    "title": lambda item: item.title.lower(),
}


def _get_place(db: Session, place_id: int) -> Place:
    place = db.get(Place, place_id)
    if place is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Место не найдено")
    return place


@router.get("", response_model=list[PlaceListItem])
def list_places(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    status_filter: str | None = Query(default=None, alias="status"),
    category: Category | None = None,
    q: str | None = None,
    sort: str = "recent",
) -> list[PlaceListItem]:
    query = select(Place)
    if category:
        query = query.where(Place.category == category)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Place.title.ilike(pattern), Place.address.ilike(pattern)))

    items = place_service.list_items(db, list(db.scalars(query)), user)
    if status_filter in {place_service.STATUS_WISH, place_service.STATUS_PLANNED, place_service.STATUS_VISITED}:
        items = [item for item in items if item.status == status_filter]
    items.sort(key=SORTS.get(sort, SORTS["recent"]))
    return items


@router.get("/roulette-pool", response_model=list[PlaceListItem])
def roulette_pool(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    category: Category | None = None,
    include_planned: bool = False,
) -> list[PlaceListItem]:
    """Места, куда мы ещё не ходили. Запланированные по умолчанию исключаем."""
    query = select(Place)
    if category:
        query = query.where(Place.category == category)
    items = place_service.list_items(db, list(db.scalars(query)), user)
    allowed = {place_service.STATUS_WISH}
    if include_planned:
        allowed.add(place_service.STATUS_PLANNED)
    pool = [item for item in items if item.status in allowed]
    random.shuffle(pool)
    return pool


@router.post("", response_model=PlaceDetail, status_code=status.HTTP_201_CREATED)
def create_place(
    payload: PlaceInput, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> PlaceDetail:
    place = Place(**payload.model_dump(), created_by_id=user.id)
    db.add(place)
    db.commit()
    db.refresh(place)
    return place_service.detail(db, place, user)


@router.get("/{place_id}", response_model=PlaceDetail)
def get_place(
    place_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> PlaceDetail:
    return place_service.detail(db, _get_place(db, place_id), user)


@router.patch("/{place_id}", response_model=PlaceDetail)
def update_place(
    place_id: int,
    payload: PlacePatch,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> PlaceDetail:
    place = _get_place(db, place_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(place, field, value)
    db.commit()
    db.refresh(place)
    return place_service.detail(db, place, user)


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(
    place_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> None:
    place = _get_place(db, place_id)
    for photo in db.scalars(select(Photo).where(Photo.place_id == place.id)):
        delete_image(photo.filename, photo.thumb_filename)
    db.delete(place)
    db.commit()


@router.put("/{place_id}/interest", response_model=PlaceDetail)
def add_interest(
    place_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> PlaceDetail:
    place = _get_place(db, place_id)
    existing = db.scalar(
        select(Interest).where(Interest.place_id == place.id, Interest.user_id == user.id)
    )
    if existing is None:
        db.add(Interest(place_id=place.id, user_id=user.id))
        db.commit()
        db.refresh(place)
    return place_service.detail(db, place, user)


@router.delete("/{place_id}/interest", response_model=PlaceDetail)
def remove_interest(
    place_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> PlaceDetail:
    place = _get_place(db, place_id)
    existing = db.scalar(
        select(Interest).where(Interest.place_id == place.id, Interest.user_id == user.id)
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
        db.refresh(place)
    return place_service.detail(db, place, user)


@router.put("/{place_id}/review", response_model=PlaceDetail)
def upsert_review(
    place_id: int,
    payload: ReviewInput,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> PlaceDetail:
    place = _get_place(db, place_id)
    review = db.scalar(select(Review).where(Review.place_id == place.id, Review.user_id == user.id))
    if review is None:
        review = Review(place_id=place.id, user_id=user.id, score=payload.score, text=payload.text)
        db.add(review)
    else:
        review.score = payload.score
        review.text = payload.text
        review.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(place)
    return place_service.detail(db, place, user)
