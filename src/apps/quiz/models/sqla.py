from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    inspect,
    Integer,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.orm.base import LoaderCallableStatus as load_status

from apps.quiz.models import (
    AnswerEntity,
    CategoryComplaintEntity,
    ComplaintEntity,
    QuestionEntity,
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

    def to_entity(self):
        """
        Преобразует ORM в объект Entity.
        Если связанный объект(ы) не подгружен из БД,
        то в поле объекта будет None или пустой список соответственно
        """
        answers = (
            self.answers
            if not inspect(self).attrs.answers.loaded_value
            == load_status.NO_VALUE
            else []
        )
        complaints = (
            self.complaints
            if not inspect(self).attrs.complaints.loaded_value
            == load_status.NO_VALUE
            else []
        )
        return QuestionEntity(
            id=self.id,
            text=self.text,
            published=self.published,
            answers=[answer.to_entity() for answer in answers],
            complaints=[complaint.to_entity() for complaint in complaints],
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

    def to_entity(self):
        """
        Преобразует ORM в объект Entity.
        Если связанный объект(ы) не подгружен из БД,
        то в поле объекта будет None или пустой список соответственно
        """
        question = (
            self.question
            if not inspect(self).attrs.question.loaded_value
            == load_status.NO_VALUE
            else None
        )
        return AnswerEntity(
            id=self.id,
            text=self.text,
            right=self.right,
            question=question.to_entity() if question else None,
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

    def to_entity(self) -> ComplaintEntity:
        """
        Преобразует ORM в объект Entity.
        Если связанный объект(ы) не подгружен из БД,
        то в поле объекта будет None или пустой список соответственно
        """
        profile = (
            self.profile
            if not inspect(self).attrs.profile.loaded_value
            == load_status.NO_VALUE
            else None
        )
        question = (
            self.question
            if not inspect(self).attrs.question.loaded_value
            == load_status.NO_VALUE
            else None
        )
        category = (
            self.category
            if not inspect(self).attrs.category.loaded_value
            == load_status.NO_VALUE
            else None
        )
        return ComplaintEntity(
            id=self.id,
            text=self.text,
            created_at=self.created_at,
            solved=self.solved,
            profile=profile.to_entity() if profile else None,
            question=question.to_entity() if question else None,
            category=category.to_entity() if category else None,
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

    def to_entity(self) -> CategoryComplaintEntity:
        """
        Преобразует ORM в объект Entity.
        Если связанный объект(ы) не подгружен из БД,
        то в поле объекта будет None или пустой список соответственно
        """
        complaints = (
            self.complaint
            if not inspect(self).attrs.complaint.loaded_value
            == load_status.NO_VALUE
            else []
        )
        return CategoryComplaintEntity(
            id=self.id,
            name=self.name,
            complaints=[c.to_entity for c in complaints],
        )
