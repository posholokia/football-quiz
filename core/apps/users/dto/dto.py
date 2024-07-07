from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserDTO:
    id: int
    username: str
    date_joined: datetime
    profile_id: int


@dataclass
class StatisticDTO:
    id: int
    games: int
    score: int
    place: int
    rights: int
    wrongs: int
    trend: int
    profile_id: int


@dataclass
class ProfileDTO:
    id: int
    name: str
    device_uuid: str
    user_id: int | None
