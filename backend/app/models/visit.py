from datetime import date, datetime, time
from enum import StrEnum

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Table, Text, Time, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, timestamp_column
from app.models.place import Place
from app.models.user import User


class VisitStatus(StrEnum):
    planned = "planned"
    done = "done"
    cancelled = "cancelled"


visit_participants = Table(
    "visit_participants",
    Base.metadata,
    Column("visit_id", ForeignKey("visits.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), index=True)
    scheduled_date: Mapped[date] = mapped_column(Date, index=True)
    scheduled_time: Mapped[time | None] = mapped_column(Time)
    status: Mapped[str] = mapped_column(String(16), default=VisitStatus.planned, index=True)
    note: Mapped[str] = mapped_column(Text, default="")
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = timestamp_column()

    place: Mapped["Place"] = relationship(lazy="joined")
    created_by: Mapped["User | None"] = relationship(lazy="joined")
    participants: Mapped[list["User"]] = relationship(secondary=visit_participants, lazy="selectin")
    photos: Mapped[list["Photo"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan", lazy="selectin"
    )


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    visit_id: Mapped[int | None] = mapped_column(ForeignKey("visits.id", ondelete="CASCADE"), index=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), index=True)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    filename: Mapped[str] = mapped_column(String(255))
    thumb_filename: Mapped[str] = mapped_column(String(255))
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    caption: Mapped[str] = mapped_column(String(300), default="")
    created_at: Mapped[datetime] = timestamp_column()

    visit: Mapped["Visit | None"] = relationship(back_populates="photos")
    uploaded_by: Mapped["User | None"] = relationship(lazy="joined")
