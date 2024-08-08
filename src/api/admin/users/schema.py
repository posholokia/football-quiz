from datetime import datetime

from pydantic import BaseModel


class ProfileStatisticAdminRetrieveSchema(BaseModel):
    id: int
    score: int
    place: int
    games: int


class ProfileAdminRetrieveSchema(BaseModel):
    id: int
    name: str
    statistic: ProfileStatisticAdminRetrieveSchema | None
    last_visit: datetime
    complaints: int
