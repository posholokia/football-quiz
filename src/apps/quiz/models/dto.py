from dataclasses import dataclass

from .entity import QuestionEntity


@dataclass
class QuestionAdminDTO(QuestionEntity):
    complaints: int = 0
