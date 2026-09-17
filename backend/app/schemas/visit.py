from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.models.visit import VisitStatus
from app.schemas.auth import UserPublic
from app.schemas.place import CategoryPublic, PhotoPublic


class VisitPlaceBrief(BaseModel):
    id: int
    title: str
    category: CategoryPublic | None
    address: str


class VisitPublic(BaseModel):
    id: int
    place: VisitPlaceBrief
    scheduled_date: date
    scheduled_time: time | None
    status: VisitStatus
    note: str
    created_by: UserPublic | None
    participants: list[UserPublic]
    photos: list[PhotoPublic]
    completed_at: datetime | None
    created_at: datetime


class VisitInput(BaseModel):
    place_id: int
    scheduled_date: date
    scheduled_time: time | None = None
    note: str = Field(default="", max_length=1000)
    participant_ids: list[int] = Field(default_factory=list)


class VisitPatch(BaseModel):
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    status: VisitStatus | None = None
    note: str | None = Field(default=None, max_length=1000)
    participant_ids: list[int] | None = None
