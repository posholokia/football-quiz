from functools import lru_cache

from punq import Container

from sqlalchemy.ext.asyncio import AsyncSession

from core.api.pagination import (
    LimitOffsetPaginator,
    R,
)
from core.apps.game_settings.actions.actions import GameSettingsActions
from core.apps.game_settings.services.storage.base import IGameSettingsService
from core.apps.game_settings.services.storage.sqla import (
    ORMGameSettingsService,
)
from core.apps.quiz.actions.actions import (
    CategoryComplaintsActions,
    ComplaintsActions,
    QuestionsActions,
)
from core.apps.quiz.permissions.quiz import DevicePermissions
from core.apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from core.apps.quiz.services.storage.sqla import (
    ORMCategoryComplaintService,
    ORMComplaintService,
    ORMQuestionsService,
)
from core.apps.users.actions import (  # CompositeProfileAction,
    CompositeStatisticAction,
    ProfileActions,
    StatisticsActions,
)
from core.apps.users.models import (
    DayStatistic,
    MonthStatistic,
    Statistic,
)
from core.apps.users.permissions.profile import ProfilePermissions
from core.apps.users.services.storage.base import (
    IProfileService,
    IStatisticService,
)
from core.apps.users.services.storage.sqla import (
    ORMProfileService,
    ORMStatisticService,
)
from core.apps.users.services.validator.profile import ProfileValidator
from core.config.database.db import SessionLocal
from core.services.security.device_validator import DeviceTokenValidate


@lru_cache(1)
def get_container() -> Container:
    return _initialize_container()


def _initialize_container() -> Container:
    container = Container()

    def build_statistic_actions() -> CompositeStatisticAction:
        return CompositeStatisticAction(
            actions=[
                container.resolve(StatisticsActions, model=Statistic),
                container.resolve(StatisticsActions, model=DayStatistic),
                container.resolve(StatisticsActions, model=MonthStatistic),
            ]
        )

    # def build_profile_actions() -> CompositeProfileAction:
    #     return CompositeProfileAction(
    #         actions=[
    #             container.resolve(ProfileActions, model=Statistic),
    #             container.resolve(ProfileActions, model=DayStatistic),
    #             container.resolve(ProfileActions, model=MonthStatistic),
    #         ]
    #     )

    container.register(AsyncSession, factory=lambda: SessionLocal())
    # orm интерфейсы
    container.register(IProfileService, ORMProfileService)

    container.register(IStatisticService, ORMStatisticService, model=Statistic)
    container.register(
        IStatisticService, ORMStatisticService, model=DayStatistic
    )
    container.register(
        IStatisticService, ORMStatisticService, model=MonthStatistic
    )

    container.register(IGameSettingsService, ORMGameSettingsService)
    container.register(IQuestionService, ORMQuestionsService)
    container.register(IComplaintService, ORMComplaintService)
    container.register(ICategoryComplaintService, ORMCategoryComplaintService)
    # валидаторы
    container.register(ProfileValidator)
    container.register(DeviceTokenValidate)
    # разрешения
    container.register(ProfilePermissions)
    container.register(DevicePermissions)
    # экшены
    # профиль
    container.register(ProfileActions)
    # container.register(CompositeProfileAction, factory=build_profile_actions)

    # статистика
    container.register(R, ORMStatisticService, model=Statistic)
    container.register(R, ORMStatisticService, model=DayStatistic)
    container.register(R, ORMStatisticService, model=MonthStatistic)

    container.register(LimitOffsetPaginator)

    container.register(StatisticsActions)
    container.register(
        CompositeStatisticAction, factory=build_statistic_actions
    )

    container.register(QuestionsActions)
    container.register(GameSettingsActions)
    container.register(ComplaintsActions)
    container.register(CategoryComplaintsActions)
    return container
