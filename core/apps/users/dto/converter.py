from core.apps.users.dto.dto import ProfileDTO, StatisticDTO
from core.apps.users.models import Profile, Statistic


async def orm_profile_to_dto(model_obj: Profile) -> ProfileDTO:
    return ProfileDTO(
        id=model_obj.id,
        name=model_obj.name,
        device_uuid=model_obj.device_uuid,
        user_id=model_obj.user_id,
    )


async def orm_statistics_to_dto(model_obj: Statistic) -> StatisticDTO:
    return StatisticDTO(
        id=model_obj.id,
        games=model_obj.games,
        score=model_obj.score,
        place=model_obj.place,
        rights=model_obj.rights,
        wrongs=model_obj.wrongs,
        profile_id=model_obj.profile_id,
    )
