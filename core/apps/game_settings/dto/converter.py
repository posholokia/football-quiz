from core.apps.game_settings.dto.dto import GameSettingsDTO
from core.apps.game_settings.models import GameSettings


async def game_settings_orm_to_dto(orm_result: GameSettings) -> GameSettingsDTO:
    return GameSettingsDTO(
        time_round=orm_result.time_round,
        question_limit=orm_result.question_limit,
        max_energy=orm_result.max_energy,
        start_energy=orm_result.start_energy,
        energy_for_ad=orm_result.energy_for_ad,
        round_cost=orm_result.round_cost,
        question_skip_cost=orm_result.question_skip_cost,
        energy_perfect_round=orm_result.energy_perfect_round,
    )
