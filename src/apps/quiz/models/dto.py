from dataclasses import dataclass

from apps.quiz.models import QuestionEntity


@dataclass
class QuestionAdminDTO(QuestionEntity):
    complaints: int = 0
