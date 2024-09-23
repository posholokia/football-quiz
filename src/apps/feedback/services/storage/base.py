from abc import ABC
from dataclasses import dataclass

from core.database.repository.base import IRepository


@dataclass
class IFeedbackService(IRepository, ABC):
    pass
