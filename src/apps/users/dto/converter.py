from apps.users.dto.dto import (
    LadderStatisticDTO,
    ProfileDTO,
    ProfileTitleDTO,
    StatisticDTO,
)
from apps.users.models import (
    BestPlayerTitle,
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
    title_dto = await orm_profile_title_to_dto(orm_result.profile.title)
    return StatisticDTO(
        id=orm_result.id,
        games=orm_result.games,
        score=orm_result.score,
        place=orm_result.place,
        rights=orm_result.rights,
        wrongs=orm_result.wrongs,
        trend=orm_result.trend,
        profile_id=orm_result.profile_id,
        title=title_dto,
    )


async def orm_ladder_to_dto(orm_result: Statistic) -> LadderStatisticDTO:
    profile_dto = await orm_profile_to_dto(orm_result.profile)
    title_dto = await orm_profile_title_to_dto(orm_result.profile.title)
    return LadderStatisticDTO(
        id=orm_result.id,
        games=orm_result.games,
        score=orm_result.score,
        place=orm_result.place,
        rights=orm_result.rights,
        wrongs=orm_result.wrongs,
        trend=orm_result.trend,
        profile=profile_dto,
        title=title_dto,
    )


async def orm_profile_title_to_dto(
    orm_result: BestPlayerTitle,
) -> ProfileTitleDTO | None:
    if orm_result is None:
        return ProfileTitleDTO(
            best_of_the_day=0,
            best_of_the_month=0,
        )

    return ProfileTitleDTO(
        best_of_the_day=orm_result.best_of_the_day,
        best_of_the_month=orm_result.best_of_the_month,
    )
