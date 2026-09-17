from collections import defaultdict
from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Photo, Place, User, Visit, VisitStatus
from app.schemas.auth import UserPublic
from app.schemas.place import (
    CategoryPublic,
    PhotoPublic,
    PlaceDetail,
    PlaceListItem,
    ReviewPublic,
    VisitBrief,
)
from app.services.media import media_url

STATUS_WISH = "wish"
STATUS_PLANNED = "planned"
STATUS_VISITED = "visited"


def photo_public(photo: Photo) -> PhotoPublic:
    return PhotoPublic(
        id=photo.id,
        url=media_url(photo.filename) or "",
        thumb_url=media_url(photo.thumb_filename) or "",
        width=photo.width,
        height=photo.height,
        caption=photo.caption,
        uploaded_by=UserPublic.model_validate(photo.uploaded_by) if photo.uploaded_by else None,
        created_at=photo.created_at,
    )


def _aggregate(db: Session, place_ids: list[int]) -> tuple[dict, dict]:
    """Возвращает визиты и фотографии, сгруппированные по месту."""
    if not place_ids:
        return {}, {}

    visits: dict[int, list[Visit]] = defaultdict(list)
    for visit in db.scalars(
        select(Visit).where(Visit.place_id.in_(place_ids)).order_by(Visit.scheduled_date)
    ):
        visits[visit.place_id].append(visit)

    photos: dict[int, list[Photo]] = defaultdict(list)
    for photo in db.scalars(
        select(Photo).where(Photo.place_id.in_(place_ids)).order_by(Photo.created_at.desc())
    ):
        photos[photo.place_id].append(photo)

    return visits, photos


def place_status(visits: list[Visit], today: date | None = None) -> tuple[str, Visit | None, date | None]:
    today = today or date.today()
    done = [v for v in visits if v.status == VisitStatus.done]
    upcoming = sorted(
        (v for v in visits if v.status == VisitStatus.planned and v.scheduled_date >= today),
        key=lambda v: (v.scheduled_date, v.scheduled_time or time.min),
    )
    last_visit = max((v.scheduled_date for v in done), default=None)

    if done:
        status = STATUS_VISITED
    elif upcoming:
        status = STATUS_PLANNED
    else:
        status = STATUS_WISH
    return status, (upcoming[0] if upcoming else None), last_visit


def _base_fields(place: Place, user: User, visits: list[Visit], photos: list[Photo]) -> dict:
    status, next_visit, last_visit_date = place_status(visits)
    scores = [review.score for review in place.reviews]
    return {
        "id": place.id,
        "title": place.title,
        "category": CategoryPublic.model_validate(place.category) if place.category else None,
        "address": place.address,
        "lat": place.lat,
        "lon": place.lon,
        "status": status,
        "interest_count": len(place.interests),
        "interested": any(i.user_id == user.id for i in place.interests),
        "photo_count": len(photos),
        "cover_url": media_url(photos[0].thumb_filename) if photos else None,
        "average_score": round(sum(scores) / len(scores), 1) if scores else None,
        "next_visit": VisitBrief(
            id=next_visit.id,
            scheduled_date=next_visit.scheduled_date,
            scheduled_time=next_visit.scheduled_time,
            status=next_visit.status,
        )
        if next_visit
        else None,
        "last_visit_date": last_visit_date,
        "created_by": UserPublic.model_validate(place.created_by) if place.created_by else None,
    }


def list_items(db: Session, places: list[Place], user: User) -> list[PlaceListItem]:
    visits, photos = _aggregate(db, [p.id for p in places])
    return [
        PlaceListItem(**_base_fields(place, user, visits.get(place.id, []), photos.get(place.id, [])))
        for place in places
    ]


def detail(db: Session, place: Place, user: User) -> PlaceDetail:
    visits, photos = _aggregate(db, [place.id])
    reviews = [ReviewPublic.model_validate(review) for review in place.reviews]
    return PlaceDetail(
        **_base_fields(place, user, visits.get(place.id, []), photos.get(place.id, [])),
        description=place.description,
        website_url=place.website_url,
        created_at=place.created_at,
        interested_by=[UserPublic.model_validate(i.user) for i in place.interests],
        reviews=sorted(reviews, key=lambda r: r.created_at, reverse=True),
        my_review=next((r for r in reviews if r.user.id == user.id), None),
    )
