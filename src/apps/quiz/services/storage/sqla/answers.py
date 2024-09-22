from dataclasses import dataclass
from typing import Type

from loguru import logger

from sqlalchemy import (
    insert,
    update,
)
from sqlalchemy.exc import IntegrityError

from apps.quiz.exceptions.answer import AnswerIntegrityError
from apps.quiz.models import AnswerEntity
from apps.quiz.services.storage.base import IAnswerService
from core.database.db import Database
from core.database.repository.base import TModel


@dataclass
class ORMAnswerService(IAnswerService):
    db: Database
    model: Type[TModel]

    async def bulk_create(
        self, data: list[dict[str, str]]
    ) -> list[AnswerEntity]:
        try:
            async with self.db.get_session() as session:
                query = insert(self.model).returning(self.model)
                result = await session.execute(query, data)
                orm_objs = result.scalars().all()
                return [obj.to_entity() for obj in orm_objs]
        except IntegrityError as e:
            logger.error(
                "Ошибка при создании ответов на вопрос: {}\nданные: {}",
                e,
                data,
            )
            raise AnswerIntegrityError()

    async def bulk_update(self, data: list[dict[str, str]]) -> None:
        async with self.db.get_session() as session:
            query = update(self.model)
            await session.execute(query, data)
