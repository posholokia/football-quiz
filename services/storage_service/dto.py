from dataclasses import dataclass


@dataclass
class UserDTO:
    id: int
    password: str
    is_superuser: bool
    is_active: bool
    username: str


@dataclass
class ProfileDTO:
    id: int
    name: str
    device_uuid: str
    user_id: int


@dataclass
class StatisticDTO:
    id: int
    games: int
    score: int
    place: int
    rights: int
    wrongs: int
    profile_id: int


@dataclass
class AnswerDTO:
    id: int
    text: str
    right: bool
    question_id: int


@dataclass
class QuestionDTO:
    id: int
    text: str
    published: bool
    answers: list[AnswerDTO]
