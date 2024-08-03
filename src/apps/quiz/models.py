from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    relationship,
)

from core.database.db import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    text = Column(Text)
    published = Column(Boolean)
    answers: Mapped[List["Answer"]] = relationship(
        "Answer", back_populates="question"
    )
    complaints: Mapped[List["Complaint"]] = relationship(
        "Complaint", back_populates="question"
    )


class Answer(Base):
    __tablename__ = "answers"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    text = Column(Text())
    right = Column(Boolean)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question = relationship("Question", back_populates="answers")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    profile = relationship("Profile", back_populates="complaints")
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question = relationship("Question", back_populates="complaints")
    text = Column(Text)
    created_at = Column(DateTime)
    solved = Column(Boolean)
    category_id = Column(
        Integer, ForeignKey("category_complaints.id"), nullable=False
    )
    category: Mapped["CategoryComplaint"] = relationship(
        "CategoryComplaint", back_populates="complaint"
    )


class CategoryComplaint(Base):
    __tablename__ = "category_complaints"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    name = Column(Text)
    complaint: Mapped[List["CategoryComplaint"]] = relationship(
        "Complaint", back_populates="category"
    )
