from functools import lru_cache

from api.pagination import (
    LimitOffsetPaginator,
    PagePaginator,
)
from punq import (
    Container,
    Scope,
)

from apps.game_settings.actions import GameSettingsActions
from apps.game_settings.services.storage.base import IGameSettingsService
from apps.game_settings.services.storage.sqla import ORMGameSettingsService
from apps.quiz.actions import (
    CategoryComplaintsActions,
    ComplaintsActions,
    QuestionsActions,
)
from apps.quiz.permissions.quiz import DevicePermissions
from apps.quiz.services.storage.base import (
    IAnswerService,
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.quiz.services.storage.sqla import (
    ORMAnswerService,
    ORMCategoryComplaintService,
    ORMComplaintService,
    ORMQuestionsService,
)
from apps.quiz.validator.answers import AnswerListValidator
from apps.users.actions import (
    AdminAuthAction,
    CompositeStatisticAction,
    ProfileActions,
    StatisticsActions,
)
from apps.users.models import (
    DayStatistic,
    MonthStatistic,
    Statistic,
)
from apps.users.permissions.admin import IsAdminUser
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
from apps.users.services.storage.base import IUserService
from apps.users.services.storage.sqla import ORMUserService
from apps.users.services.validator.profile import ProfileValidator
from config import settings
from core.database.db import Database
from core.security.fingerprint_auth.device_validator import DeviceTokenValidate
from services.redis_pool import RedisPool


@lru_cache(1)
def get_container() -> Container:
    return DiContainer().initialize_container()


class DiContainer:
    def __init__(self):
        self.container = Container()

    def initialize_container(self) -> Container:
        self.__init_orm_containers()
        self.__init_service_containers()
        self.__init_validators_containers()
        self.__init_permission_containers()
        self.__init_pagination_containers()
        self.__init_action_containers()
        return self.container

    def __init_orm_containers(self):
        # обязательно синглтон, иначе пробьет лимит по подключениям
        self.container.register(Database, scope=Scope.singleton)

        # users app
        self.container.register(IProfileService, ORMProfileService)
        self.container.register(IProfileTitleService, ORMProfileTitleService)
        self.container.register(
            IStatisticService, ORMStatisticService, model=Statistic
        )
        self.container.register(
            IStatisticService, ORMStatisticService, model=DayStatistic
        )
        self.container.register(
            IStatisticService, ORMStatisticService, model=MonthStatistic
        )
        self.container.register(IUserService, ORMUserService)

        # game_settings app
        self.container.register(IGameSettingsService, ORMGameSettingsService)

        # quiz app
        self.container.register(IQuestionService, ORMQuestionsService)
        self.container.register(IComplaintService, ORMComplaintService)
        self.container.register(
            ICategoryComplaintService, ORMCategoryComplaintService
        )
        self.container.register(IAnswerService, ORMAnswerService)

    def __init_service_containers(self):
        self.container.register(RedisPool, scope=Scope.singleton)
        self.container.register(
            ITokenStorage,
            lambda: RedisTokenStorage(
                self.container.resolve(
                    RedisPool,
                    db_number=settings.redis_db_token,
                )
            ),
        )
        self.container.register(BlacklistRefreshToken)

    def __init_validators_containers(self):
        self.container.register(ProfileValidator)
        self.container.register(DeviceTokenValidate)
        self.container.register(AnswerListValidator)

    def __init_permission_containers(self):
        self.container.register(ProfilePermissions)
        self.container.register(DevicePermissions)
        self.container.register(IsAdminUser)

    def __init_pagination_containers(self):
        self.container.register(LimitOffsetPaginator)
        self.container.register(PagePaginator)

    def __init_action_containers(self):
        self.container.register(ProfileActions)
        self.container.register(StatisticsActions)
        self.container.register(
            CompositeStatisticAction, factory=self.__build_statistic_actions
        )
        self.container.register(QuestionsActions)
        self.container.register(ComplaintsActions)
        self.container.register(CategoryComplaintsActions)
        self.container.register(GameSettingsActions)
        self.container.register(AdminAuthAction)

    def __build_statistic_actions(self) -> CompositeStatisticAction:
        return CompositeStatisticAction(
            actions=[
                self.container.resolve(StatisticsActions, model=Statistic),
                self.container.resolve(StatisticsActions, model=DayStatistic),
                self.container.resolve(
                    StatisticsActions, model=MonthStatistic
                ),
            ]
        )


# def _initialize_container() -> Container:
#     container = Container()
#
#     def build_statistic_actions() -> CompositeStatisticAction:
#         return CompositeStatisticAction(
#             actions=[
#                 container.resolve(StatisticsActions, model=Statistic),
#                 container.resolve(StatisticsActions, model=DayStatistic),
#                 container.resolve(StatisticsActions, model=MonthStatistic),
#             ]
#         )
#
#     # обязательно синглтон, иначе пробьет лимит по подключениям
#     container.register(Database, scope=Scope.singleton)
#
#     """------------------------------orm интерфейсы------------------------------"""
#     container.register(IProfileService, ORMProfileService)
#     container.register(IProfileTitleService, ORMProfileTitleService)
#     container.register(IStatisticService, ORMStatisticService, model=Statistic)
#     container.register(
#         IStatisticService, ORMStatisticService, model=DayStatistic
#     )
#     container.register(
#         IStatisticService, ORMStatisticService, model=MonthStatistic
#     )
#
#     container.register(IGameSettingsService, ORMGameSettingsService)
#     container.register(IQuestionService, ORMQuestionsService)
#     container.register(IComplaintService, ORMComplaintService)
#     container.register(ICategoryComplaintService, ORMCategoryComplaintService)
#     container.register(R, ORMStatisticService, model=Statistic)
#     container.register(R, ORMStatisticService, model=DayStatistic)
#     container.register(R, ORMStatisticService, model=MonthStatistic)
#     container.register(IUserService, ORMUserService)
#     """------------------------------сервисы------------------------------"""
#     container.register(RedisPool, scope=Scope.singleton)
#     container.register(
#         ITokenStorage,
#         lambda: RedisTokenStorage(
#             container.resolve(RedisPool, db_number=settings.redis_db_token)
#         ),
#     )
#     container.register(BlacklistRefreshToken)
#
#     """------------------------------валидаторы------------------------------"""
#     container.register(ProfileValidator)
#     container.register(DeviceTokenValidate)
#
#     """------------------------------разрешения------------------------------"""
#     container.register(ProfilePermissions)
#     container.register(DevicePermissions)
#
#     """------------------------------экшены------------------------------"""
#     # пагинаторы
#     container.register(LimitOffsetPaginator)
#     # профиль
#     container.register(ProfileActions)
#     # статистика
#     container.register(StatisticsActions)
#     container.register(
#         CompositeStatisticAction, factory=build_statistic_actions
#     )
#     # викторина
#     container.register(QuestionsActions)
#     container.register(ComplaintsActions)
#     container.register(CategoryComplaintsActions)
#
#     # настройки
#     container.register(GameSettingsActions)
#     container.register(UserAuthAction)
#
#     return container
