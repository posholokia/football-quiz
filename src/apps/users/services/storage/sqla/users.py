from dataclasses import dataclass

from apps.users.services.storage.base import IUserService
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMUserService(CommonRepository, IUserService):
    pass
