from services.storage_service.dto import StatisticDTO, ProfileDTO
from sqlalchemy.engine.row import Row

from apps.users.models import Statistic, Profile


async def statistics_orm_row_to_entity(orm_result: Row) -> StatisticDTO:
    return StatisticDTO(
        id=orm_result.id,
        games=orm_result.games,
        score=orm_result.score,
        place=orm_result.place,
        rights=orm_result.rights,
        wrongs=orm_result.wrongs,
        profile_id=orm_result.profile_id,
    )


async def statistics_entity_to_orm(entity: StatisticDTO) -> Statistic:
    return Statistic(
        id=entity.id,
        games=entity.games,
        score=entity.score,
        place=entity.place,
        rights=entity.rights,
        wrongs=entity.wrongs,
        profile_id=entity.profile_id,
    )


async def profile_model_to_dto(profile: Profile) -> ProfileDTO:
    return ProfileDTO(
        id=profile.id,
        name=profile.name,
        device_uuid=profile.device_uuid,
        user_id=profile.user_id,
    )


async def profile_orm_row_to_entity(orm_result: Row) -> ProfileDTO:
    return ProfileDTO(
        id=orm_result.id,
        name=orm_result.name,
        device_uuid=orm_result.device_uuid,
        user_id=orm_result.id,
    )
