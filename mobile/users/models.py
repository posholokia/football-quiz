from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    sql,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from core.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    password = Column(String(128))
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    username = Column(String(256), unique=True)
    date_joined = Column(DateTime, server_default=sql.func.now())
    profile = relationship(
        "Profile", uselist=False, back_populates="user"
    )


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    name = Column(String(50))
    device_uuid = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="profile")
    statistic = relationship(
        "Statistic", uselist=False, back_populates="profile"
    )

    __table_args__ = (UniqueConstraint("user_id"),)


class Statistic(Base):
    __tablename__ = "statictics"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    games = Column(Integer, default=0)
    score = Column(Integer, default=0)
    place = Column(Integer)
    rights = Column(Integer, default=0)
    wrongs = Column(Integer, default=0)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    profile = relationship("Profile", back_populates="statistic")

    __table_args__ = (UniqueConstraint("profile_id"),)
