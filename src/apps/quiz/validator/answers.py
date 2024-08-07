from dataclasses import dataclass

from api.admin.quiz.schema import AnswerAdminBaseSchema

from apps.quiz.exceptions import AnswerRightVariableError
from apps.quiz.exceptions.answer import (
    AnswerNotEnoughError,
    AnswerNotUniqueError,
)
from core.constructor.validators import BaseValidator


@dataclass
class AnswerListValidator(BaseValidator):
    async def validate(
        self,
        answer_list: list[AnswerAdminBaseSchema],
    ) -> None:
        self.check_length_answer(answer_list)
        self.check_only_right_answer(answer_list)
        self.check_unique_answer(answer_list)

    @staticmethod
    def check_only_right_answer(answers: list[AnswerAdminBaseSchema]) -> None:
        if (count := sum(1 for answer in answers if answer.right)) != 1:
            raise AnswerRightVariableError(
                detail=(
                    f"Может быть только один правильный вариант ответа, "
                    f"получено {count} правильных ответов."
                )
            )

    @staticmethod
    def check_unique_answer(answers: list[AnswerAdminBaseSchema]) -> None:
        answers = answers.copy()
        answers.sort(key=lambda x: x.text)
        for i in range(len(answers) - 1):
            if answers[i].text == answers[i + 1].text:
                raise AnswerNotUniqueError()

    @staticmethod
    def check_length_answer(answers: list[AnswerAdminBaseSchema]) -> None:
        if len(answers) != 4:
            raise AnswerNotEnoughError()
