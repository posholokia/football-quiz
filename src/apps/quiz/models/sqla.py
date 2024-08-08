from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from apps.users.models import Profile
from core.database.db import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    text: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(Boolean)
    answers: Mapped[List["Answer"]] = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete",
        passive_deletes=True,
    )
    complaints: Mapped[List["Complaint"]] = relationship(
        "Complaint",
        back_populates="question",
        cascade="all, delete",
        passive_deletes=True,
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    text: Mapped[str] = mapped_column(Text)
    right: Mapped[bool] = mapped_column(Boolean)
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question = relationship(
        "Question",
        back_populates="answers",
    )


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("profiles.id"), nullable=True
    )
    profile: Mapped[Profile] = relationship(
        "Profile", back_populates="complaints"
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[Question] = relationship(
        "Question",
        back_populates="complaints",
    )
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    solved: Mapped[bool] = mapped_column(Boolean)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("category_complaints.id"), nullable=False
    )
    category: Mapped["CategoryComplaint"] = relationship(
        "CategoryComplaint", back_populates="complaint"
    )


class CategoryComplaint(Base):
    __tablename__ = "category_complaints"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(Text)
    complaint: Mapped[List["CategoryComplaint"]] = relationship(
        "Complaint", back_populates="category"
    )
