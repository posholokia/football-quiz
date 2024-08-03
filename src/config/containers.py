from functools import lru_cache

from api.pagination import (
    LimitOffsetPaginator,
    R,
)
from punq import (
    Container,
    Scope,
)

from apps.game_settings.actions.actions import GameSettingsActions
from apps.game_settings.services.storage.base import IGameSettingsService
from apps.game_settings.services.storage.sqla import ORMGameSettingsService
from apps.quiz.actions.actions import (
    CategoryComplaintsActions,
    ComplaintsActions,
    QuestionsActions,
)
from apps.quiz.permissions.quiz import DevicePermissions
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.quiz.services.storage.sqla import (
    ORMCategoryComplaintService,
    ORMComplaintService,
    ORMQuestionsService,
)
from apps.users.actions import (
    CompositeStatisticAction,
    ProfileActions,
    StatisticsActions,
)
from apps.users.models import (
    DayStatistic,
    MonthStatistic,
    Statistic,
)
from apps.users.permissions.profile import ProfilePermissions
from apps.users.services.auth.jwt_auth.models import BlacklistRefreshToken
from apps.users.services.auth.jwt_auth.storage.base import ITokenStorage
from apps.users.services.auth.jwt_auth.storage.cache import RedisTokenStorage
from apps.users.services.storage import (
    IProfileService,
    IProfileTitleService,
    IStatisticService,
    ORMProfileService,
    ORMProfileTitleService,
    ORMStatisticService,
)
from apps.users.services.validator.profile import ProfileValidator
from core.database.db import Database
from core.security.fingerprint_auth.device_validator import DeviceTokenValidate
from services.redis_pool import RedisPool


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

    # обязательно синглтон, иначе пробьет лимит по подключениям
    container.register(Database, scope=Scope.singleton)
    """------------------------------orm интерфейсы------------------------------"""
    container.register(IProfileService, ORMProfileService)
    container.register(IProfileTitleService, ORMProfileTitleService)
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
    container.register(R, ORMStatisticService, model=Statistic)
    container.register(R, ORMStatisticService, model=DayStatistic)
    container.register(R, ORMStatisticService, model=MonthStatistic)

    """------------------------------валидаторы------------------------------"""
    container.register(ProfileValidator)
    container.register(DeviceTokenValidate)

    """------------------------------разрешения------------------------------"""
    container.register(ProfilePermissions)
    container.register(DevicePermissions)

    """------------------------------экшены------------------------------"""
    # пагинаторы
    container.register(LimitOffsetPaginator)
    # профиль
    container.register(ProfileActions)
    # статистика
    container.register(StatisticsActions)
    container.register(
        CompositeStatisticAction, factory=build_statistic_actions
    )
    # викторина
    container.register(QuestionsActions)
    container.register(ComplaintsActions)
    container.register(CategoryComplaintsActions)

    # настройки
    container.register(GameSettingsActions)

    """------------------------------сервисы------------------------------"""
    container.register(RedisPool)
    container.register(ITokenStorage, RedisTokenStorage)
    container.register(BlacklistRefreshToken)
    return container
