from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Place, User, Visit, VisitStatus
from app.schemas.visit import VisitInput, VisitPatch, VisitPublic
from app.services.media import delete_image
from app.services.places import photo_public

router = APIRouter(prefix="/visits", tags=["visits"])


def _get_visit(db: Session, visit_id: int) -> Visit:
    visit = db.get(Visit, visit_id)
    if visit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Поход не найден")
    return visit


def _public(visit: Visit) -> VisitPublic:
    return VisitPublic(
        id=visit.id,
        place={
            "id": visit.place.id,
            "title": visit.place.title,
            "category": visit.place.category,
            "address": visit.place.address,
        },
        scheduled_date=visit.scheduled_date,
        scheduled_time=visit.scheduled_time,
        status=visit.status,
        note=visit.note,
        created_by=visit.created_by,
        participants=visit.participants,
        photos=[photo_public(photo) for photo in sorted(visit.photos, key=lambda p: p.created_at)],
        completed_at=visit.completed_at,
        created_at=visit.created_at,
    )


def _resolve_participants(db: Session, ids: list[int]) -> list[User]:
    if not ids:
        return []
    return list(db.scalars(select(User).where(User.id.in_(ids))))


@router.get("", response_model=list[VisitPublic])
def list_visits(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    place_id: int | None = None,
    upcoming: bool = Query(default=False),
    visit_status: VisitStatus | None = Query(default=None, alias="status"),
) -> list[VisitPublic]:
    query = select(Visit)
    if place_id:
        query = query.where(Visit.place_id == place_id)
    if visit_status:
        query = query.where(Visit.status == visit_status)
    if upcoming:
        query = query.where(
            Visit.status == VisitStatus.planned, Visit.scheduled_date >= date.today()
        ).order_by(Visit.scheduled_date, Visit.scheduled_time)
    else:
        query = query.order_by(Visit.scheduled_date.desc(), Visit.id.desc())
    return [_public(visit) for visit in db.scalars(query)]


@router.post("", response_model=VisitPublic, status_code=status.HTTP_201_CREATED)
def create_visit(
    payload: VisitInput, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> VisitPublic:
    if db.get(Place, payload.place_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Место не найдено")

    visit = Visit(
        place_id=payload.place_id,
        scheduled_date=payload.scheduled_date,
        scheduled_time=payload.scheduled_time,
        note=payload.note,
        created_by_id=user.id,
    )
    participant_ids = set(payload.participant_ids) | {user.id}
    visit.participants = _resolve_participants(db, list(participant_ids))
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return _public(visit)


@router.patch("/{visit_id}", response_model=VisitPublic)
def update_visit(
    visit_id: int,
    payload: VisitPatch,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> VisitPublic:
    visit = _get_visit(db, visit_id)
    fields = payload.model_dump(exclude_unset=True)

    if "participant_ids" in fields:
        visit.participants = _resolve_participants(db, fields.pop("participant_ids") or [])
    if "status" in fields:
        new_status = fields.pop("status")
        visit.status = new_status
        visit.completed_at = datetime.now(timezone.utc) if new_status == VisitStatus.done else None
    for field, value in fields.items():
        setattr(visit, field, value)

    db.commit()
    db.refresh(visit)
    return _public(visit)


@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_visit(
    visit_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> None:
    visit = _get_visit(db, visit_id)
    for photo in visit.photos:
        delete_image(photo.filename, photo.thumb_filename)
    db.delete(visit)
    db.commit()
