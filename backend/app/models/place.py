from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, timestamp_column, utcnow
from app.models.user import User


class Category(StrEnum):
    bar = "bar"
    cafe = "cafe"
    restaurant = "restaurant"
    culture = "culture"
    activity = "activity"
    nature = "nature"
    other = "other"


class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    category: Mapped[str] = mapped_column(String(32), default=Category.other, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(String(300), default="")
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    website_url: Mapped[str | None] = mapped_column(String(500))
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = timestamp_column()
    updated_at: Mapped[datetime] = timestamp_column(onupdate=utcnow)

    created_by: Mapped["User | None"] = relationship(lazy="joined")
    interests: Mapped[list["Interest"]] = relationship(
        back_populates="place", cascade="all, delete-orphan", lazy="selectin"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="place", cascade="all, delete-orphan", lazy="selectin"
    )


class Interest(Base):
    __tablename__ = "interests"
    __table_args__ = (UniqueConstraint("place_id", "user_id", name="uq_interest_place_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = timestamp_column()

    place: Mapped["Place"] = relationship(back_populates="interests")
    user: Mapped["User"] = relationship(lazy="joined")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("place_id", "user_id", name="uq_review_place_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    score: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = timestamp_column()
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    place: Mapped["Place"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(lazy="joined")
