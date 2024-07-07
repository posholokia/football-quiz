from core.apps.users.dto.dto import (
    ProfileDTO,
    StatisticDTO,
)
from core.apps.users.models import (
    Profile,
    Statistic,
)


async def orm_profile_to_dto(orm_result: Profile) -> ProfileDTO:
    return ProfileDTO(
        id=orm_result.id,
        name=orm_result.name,
        device_uuid=orm_result.device_uuid,
        user_id=orm_result.user_id,
    )


async def orm_statistics_to_dto(orm_result: Statistic) -> StatisticDTO:
    return StatisticDTO(
        id=orm_result.id,
        games=orm_result.games,
        score=orm_result.score,
        place=orm_result.place,
        rights=orm_result.rights,
        wrongs=orm_result.wrongs,
        trend=orm_result.trend,
        profile_id=orm_result.profile_id,
    )
