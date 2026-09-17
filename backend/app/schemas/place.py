from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.models.place import Category
from app.schemas.auth import UserPublic


class PhotoPublic(BaseModel):
    id: int
    url: str
    thumb_url: str
    width: int
    height: int
    caption: str
    uploaded_by: UserPublic | None
    created_at: datetime


class ReviewPublic(BaseModel):
    id: int
    score: int
    text: str
    user: UserPublic
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewInput(BaseModel):
    score: int = Field(ge=1, le=5)
    text: str = Field(default="", max_length=2000)


class VisitBrief(BaseModel):
    id: int
    scheduled_date: date
    scheduled_time: time | None
    status: str


class PlaceInput(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    category: Category = Category.other
    description: str = Field(default="", max_length=4000)
    address: str = Field(default="", max_length=300)
    lat: float | None = None
    lon: float | None = None
    website_url: str | None = Field(default=None, max_length=500)


class PlacePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    category: Category | None = None
    description: str | None = Field(default=None, max_length=4000)
    address: str | None = Field(default=None, max_length=300)
    lat: float | None = None
    lon: float | None = None
    website_url: str | None = Field(default=None, max_length=500)


class PlaceListItem(BaseModel):
    id: int
    title: str
    category: Category
    address: str
    lat: float | None
    lon: float | None
    status: str
    interest_count: int
    interested: bool
    photo_count: int
    cover_url: str | None
    average_score: float | None
    next_visit: VisitBrief | None
    last_visit_date: date | None
    created_by: UserPublic | None


class PlaceDetail(PlaceListItem):
    description: str
    website_url: str | None
    created_at: datetime
    interested_by: list[UserPublic]
    reviews: list[ReviewPublic]
    my_review: ReviewPublic | None


class GeoSuggestion(BaseModel):
    title: str
    address: str
    lat: float | None
    lon: float | None
