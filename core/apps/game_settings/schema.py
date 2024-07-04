from pydantic import BaseModel

from core.apps.mapper import PydanticMapper


class GameSettingsSchema(PydanticMapper, BaseModel):
    time_round: int
    question_limit: int
    max_energy: int
    start_energy: int
    energy_for_ad: int
    round_cost: int
    question_skip_cost: int
    energy_perfect_round: int
    recovery_period: int
    recovery_value: int
    right_ratio: float
    wrong_ratio: float
