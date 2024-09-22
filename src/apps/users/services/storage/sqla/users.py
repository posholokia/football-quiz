from dataclasses import dataclass
from typing import Type

from apps.users.services.storage.base import (
    IUserService,
    TModel,
)
from core.database.db import Database
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMUserService(CommonRepository, IUserService):
    db: Database
    model: Type[TModel]
