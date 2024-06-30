from dataclasses import dataclass


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
