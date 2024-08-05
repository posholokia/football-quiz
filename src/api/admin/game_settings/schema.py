from pydantic import BaseModel


class GameSettingsAdminSchema(BaseModel):
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


class GameSettingsUpdateSchema(BaseModel):
    time_round: int | None = None
    question_limit: int | None = None
    max_energy: int | None = None
    start_energy: int | None = None
    energy_for_ad: int | None = None
    round_cost: int | None = None
    question_skip_cost: int | None = None
    energy_perfect_round: int | None = None
    recovery_period: int | None = None
    recovery_value: int | None = None
    right_ratio: float | None = None
    wrong_ratio: float | None = None
