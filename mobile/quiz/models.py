from typing import List

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship, Mapped

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
