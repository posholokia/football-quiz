from apps.users.models import (
    BestPlayerTitle,
    BestPlayerTitleEntity,
    Profile,
    ProfileEntity,
    Statistic,
    StatisticEntity,
    User,
    UserEntity,
)
from apps.users.models.dto import (
    LadderStatisticDTO,
    TitleStatisticDTO,
)


async def orm_profile_to_entity(orm_result: Profile) -> ProfileEntity:
    return ProfileEntity(
        id=orm_result.id,
        name=orm_result.name,
        device_uuid=orm_result.device_uuid,
    )


async def orm_statistics_to_entity(orm_result: Statistic) -> StatisticEntity:
    return StatisticEntity(
        id=orm_result.id,
        games=orm_result.games,
        score=orm_result.score,
        place=orm_result.place,
        rights=orm_result.rights,
        wrongs=orm_result.wrongs,
        perfect_rounds=orm_result.perfect_rounds,
        trend=orm_result.trend,
    )


async def orm_title_statistics_to_dto(
    orm_result: Statistic,
) -> TitleStatisticDTO:
    title_dto = await orm_profile_title_to_entity(orm_result.profile.title)
    return TitleStatisticDTO(
        id=orm_result.id,
        games=orm_result.games,
        score=orm_result.score,
        place=orm_result.place,
        rights=orm_result.rights,
        wrongs=orm_result.wrongs,
        perfect_rounds=orm_result.perfect_rounds,
        trend=orm_result.trend,
        title=title_dto,
    )


async def orm_ladder_to_dto(orm_result: Statistic) -> LadderStatisticDTO:
    profile_dto = await orm_profile_to_entity(orm_result.profile)
    title_dto = await orm_profile_title_to_entity(orm_result.profile.title)
    return LadderStatisticDTO(
        id=orm_result.id,
        games=orm_result.games,
        score=orm_result.score,
        place=orm_result.place,
        rights=orm_result.rights,
        wrongs=orm_result.wrongs,
        perfect_rounds=orm_result.perfect_rounds,
        trend=orm_result.trend,
        profile=profile_dto,
        title=title_dto,
    )


async def orm_profile_title_to_entity(
    orm_result: BestPlayerTitle,
) -> BestPlayerTitleEntity:
    if orm_result is None:
        return BestPlayerTitleEntity(
            best_of_the_day=0,
            best_of_the_month=0,
        )

    return BestPlayerTitleEntity(
        best_of_the_day=orm_result.best_of_the_day,
        best_of_the_month=orm_result.best_of_the_month,
    )


async def orm_user_to_entity(orm_result: User) -> UserEntity:
    return UserEntity(
        id=orm_result.id,
        password=orm_result.password,
        is_superuser=orm_result.is_superuser,
        is_active=orm_result.is_active,
        username=orm_result.username,
    )
