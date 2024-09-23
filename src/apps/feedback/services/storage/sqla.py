from dataclasses import dataclass

from apps.feedback.services.storage.base import IFeedbackService
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMFeedbackService(CommonRepository, IFeedbackService):
    pass
