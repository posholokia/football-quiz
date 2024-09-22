from dataclasses import dataclass
from typing import (
    Generic,
    Type,
)

from sqlalchemy import (
    delete,
    exists,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.exc import (
    IntegrityError,
    NoResultFound,
)

from core.database.db import Database
from core.database.repository.base import (
    IRepository,
    TModel,
)


@dataclass
class CommonRepository(IRepository, Generic[TModel]):
    db: Database
    model: Type[TModel]

    async def create(self, **data):
        async with self.db.get_session() as session:
            query = insert(self.model).values(**data).returning(self.model)
            result = await session.execute(query)
            obj = result.scalar()
            return obj.to_entity()

    async def get_count(self) -> int:
        async with self.db.get_ro_session() as session:
            query = select(func.count(self.model.id))
            result = await session.execute(query)
            return result.scalar_one()

    async def get_one(self, **filter_by):
        async with self.db.get_ro_session() as session:
            query = select(self.model).filter_by(**filter_by)
            results = await session.execute(query)
            obj = results.scalar()
            return obj.to_entity() if obj else None

    async def get_list(self, **filter_by):
        async with self.db.get_ro_session() as session:
            query = select(self.model).filter_by(**filter_by)
            results = await session.execute(query)
            obj_list = results.scalars().all()
            return [obj.to_entity() for obj in obj_list]

    async def update(self, pk, **fields):
        async with self.db.get_session() as session:
            query = (
                update(self.model)
                .filter_by(id=pk)
                .values(**fields)
                .returning(self.model)
            )
            result = await session.execute(query)
            obj = result.scalar()

            return obj.to_entity() if obj else None

    async def get_or_create(self, **fields):
        async with self.db.get_session() as session:
            try:
                query = select(self.model).filter_by(**fields)
                res = await session.execute(query)
                return res.one()[0].to_entity()
            except NoResultFound:
                try:
                    query = (
                        insert(self.model)
                        .values(**fields)
                        .returning(self.model)
                    )
                    result = await session.execute(query)
                    obj = result.one()[0]
                    return obj.to_entity()
                except IntegrityError:
                    await session.rollback()
                    query = select(self.model).filter_by(**fields)
                    res = await session.execute(query)
                    obj = res.one()[0]
                    return obj.to_entity()

    async def exists(self, **filter_by) -> bool | None:
        async with self.db.get_ro_session() as session:
            query = select(exists(self.model)).filter_by(**filter_by)
            return await session.scalar(query)

    async def delete(self, pk: int) -> None:
        async with self.db.get_session() as session:
            query = delete(self.model).where(self.model == pk)
            await session.execute(query)
