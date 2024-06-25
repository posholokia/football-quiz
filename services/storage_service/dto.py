from dataclasses import dataclass
from datetime import datetime


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


@dataclass
class GameSettingsDTO:
    time_round: int
    question_limit: int
    max_energy: int
    start_energy: int
    energy_for_ad: int
    round_cost: int
    question_skip_cost: int
    energy_perfect_round: int


@dataclass
class ComplaintDTO:
    id: int
    text: str
    created_at: datetime
    solved: bool
    question: QuestionDTO
    profile: ProfileDTO
