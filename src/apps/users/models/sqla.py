from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    sql,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.functions import func

from core.database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    password: Mapped[str] = mapped_column(String(128))
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    username: Mapped[str] = mapped_column(String(256), unique=True)
    date_joined: Mapped[datetime] = mapped_column(
        DateTime, server_default=sql.func.now()
    )
    profile = relationship("Profile", uselist=False, back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(String(50))
    device_uuid: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    last_visit: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    user = relationship("User", back_populates="profile")
    statistic = relationship(
        "Statistic", uselist=False, back_populates="profile"
    )
    month_statistic = relationship(
        "MonthStatistic", uselist=False, back_populates="profile"
    )
    day_statistic = relationship(
        "DayStatistic", uselist=False, back_populates="profile"
    )
    complaints = relationship("Complaint", back_populates="profile")
    title = relationship(
        "BestPlayerTitle", uselist=False, back_populates="profile"
    )

    __table_args__ = (UniqueConstraint("user_id"),)


class Statistic(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    games: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)
    place: Mapped[int] = mapped_column(Integer)
    rights: Mapped[int] = mapped_column(Integer, default=0)
    wrongs: Mapped[int] = mapped_column(Integer, default=0)
    trend: Mapped[int] = mapped_column(Integer, default=0)
    perfect_rounds: Mapped[int] = mapped_column(Integer, default=0)
    profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("profiles.id"), nullable=False
    )
    profile = relationship("Profile", back_populates="statistic")

    __table_args__ = (UniqueConstraint("profile_id"),)


class MonthStatistic(Base):
    __tablename__ = "month_statistics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    games: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)
    place: Mapped[int] = mapped_column(Integer)
    rights: Mapped[int] = mapped_column(Integer, default=0)
    wrongs: Mapped[int] = mapped_column(Integer, default=0)
    trend: Mapped[int] = mapped_column(Integer, default=0)
    perfect_rounds: Mapped[int] = mapped_column(Integer, default=0)
    profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("profiles.id"), nullable=False
    )
    profile = relationship("Profile", back_populates="month_statistic")

    __table_args__ = (UniqueConstraint("profile_id"),)


class DayStatistic(Base):
    __tablename__ = "day_statistics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    games: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)
    place: Mapped[int] = mapped_column(Integer)
    rights: Mapped[int] = mapped_column(Integer, default=0)
    wrongs: Mapped[int] = mapped_column(Integer, default=0)
    trend: Mapped[int] = mapped_column(Integer, default=0)
    perfect_rounds: Mapped[int] = mapped_column(Integer, default=0)
    profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("profiles.id"), nullable=False
    )
    profile = relationship("Profile", back_populates="day_statistic")

    __table_args__ = (UniqueConstraint("profile_id"),)


class BestPlayerTitle(Base):
    __tablename__ = "best_player_title"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    best_of_the_day: Mapped[int] = mapped_column(Integer, default=0)
    best_of_the_month: Mapped[int] = mapped_column(Integer, default=0)
    profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("profiles.id"), nullable=False
    )
    profile = relationship("Profile", back_populates="title")

    __table_args__ = (UniqueConstraint("profile_id"),)
