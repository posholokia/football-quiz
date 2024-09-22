from api.admin.users.schema import (
    ProfileAdminRetrieveSchema,
    ProfileStatisticAdminRetrieveSchema,
)

from apps.users.models import ProfileEntity


def convert_to_profile_retrieve_admin(
    profile: ProfileEntity, complaints_count: int
) -> ProfileAdminRetrieveSchema:
    if profile.statistic is None:
        statistic = None
    else:
        statistic = ProfileStatisticAdminRetrieveSchema(
            id=profile.statistic.id,
            score=profile.statistic.score,
            place=profile.statistic.place,
            games=profile.statistic.games,
        )
    return ProfileAdminRetrieveSchema(
        id=profile.id,
        name=profile.name,
        statistic=statistic,
        last_visit=profile.last_visit,
        complaints=complaints_count,
    )
