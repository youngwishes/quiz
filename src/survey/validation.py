from typing import Iterator, Callable, Generator

from rest_framework.exceptions import ValidationError


class BaseValidationService(object):
    @property
    def checkers(self) -> Iterator[Callable]:
        return (
            getattr(self, validator)
            for validator in dir(self)
            if validator.startswith("check_")
        )

    def run_validation_checkers(self) -> None:
        for checker in self.checkers:
            checker()


class QuizValidationService(BaseValidationService):
    def __init__(self, data: list[dict]) -> None:
        self.questions = data

    @property
    def question_ids(self) -> set[id]:
        return {question.get("_id") for question in self.questions}

    @property
    def answers(self) -> Generator:
        for question in self.questions:
            if answers := question.get("answers"):
                for answer in answers:
                    yield answer

    @property
    def next_question_ids(self) -> set[id]:
        return {
            answer.get("next_question_id")
            for answer in self.answers if isinstance(answer.get("next_question_id"), int)
        }

    def check_next_question_id(self) -> None:

        if self.next_question_ids.difference(self.question_ids):
            raise ValidationError(detail={"detail": "No Question matches the given query."})
