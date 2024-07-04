from core.apps.game_settings.dto.dto import GameSettingsDTO
from core.apps.game_settings.models import GameSettings


async def game_settings_orm_to_dto(
    orm_result: GameSettings,
) -> GameSettingsDTO:
    return GameSettingsDTO(
        time_round=orm_result.time_round,
        question_limit=orm_result.question_limit,
        max_energy=orm_result.max_energy,
        start_energy=orm_result.start_energy,
        energy_for_ad=orm_result.energy_for_ad,
        round_cost=orm_result.round_cost,
        question_skip_cost=orm_result.question_skip_cost,
        energy_perfect_round=orm_result.energy_perfect_round,
        recovery_period=orm_result.recovery_period,
        recovery_value=orm_result.recovery_value,
        right_ratio=orm_result.right_ratio,
        wrong_ratio=orm_result.wrong_ratio,
    )
