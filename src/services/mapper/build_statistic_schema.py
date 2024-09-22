from api.mobile.users.schema import (
    LadderStatisticRetrieveSchema,
    ProfileSchema,
    ProfileTitleRetrieveSchema,
    StatisticsRetrieveSchema,
)

from apps.users.models import (
    BestPlayerTitleEntity,
    StatisticEntity,
)


def convert_to_statistic_retrieve_mobile(
    statistic: StatisticEntity, title: BestPlayerTitleEntity
) -> StatisticsRetrieveSchema:
    return StatisticsRetrieveSchema(
        id=statistic.id,
        games=statistic.games,
        score=statistic.score,
        rights=statistic.rights,
        wrongs=statistic.wrongs,
        place=statistic.place,
        perfect_rounds=statistic.perfect_rounds,
        trend=statistic.trend,
        title=ProfileTitleRetrieveSchema(
            best_of_the_day=title.best_of_the_day,
            best_of_the_month=title.best_of_the_month,
        ),
    )


def convert_to_ladder_statistic(
    statistic: StatisticEntity,
) -> LadderStatisticRetrieveSchema:
    return LadderStatisticRetrieveSchema(
        id=statistic.id,
        games=statistic.games,
        score=statistic.score,
        rights=statistic.rights,
        wrongs=statistic.wrongs,
        place=statistic.place,
        perfect_rounds=statistic.perfect_rounds,
        trend=statistic.trend,
        title=ProfileTitleRetrieveSchema(
            best_of_the_day=statistic.profile.title.best_of_the_day,
            best_of_the_month=statistic.profile.title.best_of_the_month,
        ),
        profile=ProfileSchema(
            id=statistic.profile.id,
            name=statistic.profile.name,
        ),
    )
