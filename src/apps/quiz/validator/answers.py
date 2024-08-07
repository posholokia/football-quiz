from dataclasses import dataclass

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
        answers: list[dict[str, str | bool]],
    ) -> None:
        self.check_length_answer(answers)
        self.check_only_right_answer(answers)
        self.check_unique_answer(answers)

    @staticmethod
    def check_only_right_answer(
        answers: list[dict[str, str | bool]],
    ) -> None:
        if (count := sum(1 for answer in answers if answer["right"])) != 1:
            raise AnswerRightVariableError(
                detail=(
                    f"Может быть только один правильный вариант ответа, "
                    f"получено {count} правильных ответов."
                )
            )

    @staticmethod
    def check_unique_answer(
        answers: list[dict[str, str | bool]],
    ) -> None:
        answers = answers.copy()
        answers.sort(key=lambda x: x["text"])
        for i in range(len(answers) - 1):
            if answers[i]["text"] == answers[i + 1]["text"]:
                raise AnswerNotUniqueError()

    @staticmethod
    def check_length_answer(answers: list[dict[str, str | bool]]) -> None:
        if len(answers) != 4:
            raise AnswerNotEnoughError()
