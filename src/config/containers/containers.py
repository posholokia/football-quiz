from functools import lru_cache

from apps.game_settings.actions import GameSettingsActions
from apps.game_settings.models import GameSettings
from apps.game_settings.services.storage.base import IGameSettingsService
from apps.game_settings.services.storage.sqla import ORMGameSettingsService
from apps.quiz.actions import (
    CategoryComplaintsActions,
    ComplaintsActions,
    QuestionsActions,
)
from apps.quiz.models import (
    Answer,
    CategoryComplaint,
    Complaint,
    Question,
)
from apps.quiz.permissions.quiz import DevicePermissions
from apps.quiz.services.storage.base import (
    IAnswerService,
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.quiz.services.storage.sqla import (
    ORMCategoryComplaintService,
    ORMComplaintService,
    ORMQuestionsService,
)
from apps.quiz.services.storage.sqla.answers import ORMAnswerService
from apps.quiz.validator.answers import AnswerListValidator
from apps.users.actions import (
    AdminAuthAction,
    CompositeStatisticAction,
    ProfileActions,
    StatisticsActions,
)
from apps.users.models import (
    BestPlayerTitle,
    DayStatistic,
    MonthStatistic,
    Profile,
    Statistic,
    User,
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
from apps.users.validator.profile import (
    ProfileValidator,
    ProfileValidatorLocal,
)
from config import settings
from config.base_settings.common import EnvironVariables
from config.containers.di import (
    Container,
    ContainerBuilder,
    Dependency as Dep,
    Scope,
    TestContainer,
)
from core.database.db import (
    Database,
    DatabaseConnection,
    Transaction,
)
from core.security.fingerprint_auth.device_validator import DeviceTokenValidate
from services.redis_pool import RedisPool


@lru_cache(1)
def get_container() -> Container:
    match settings.environ:
        case EnvironVariables.local:
            return _get_local_container()
        case EnvironVariables.prod:
            return _get_main_container()
        case EnvironVariables.test:
            return _get_test_container()
    raise Exception("Для этого типа окружения не установлен контейнер")


def _get_main_container() -> Container:
    return DiContainer().initialize_container()


def _get_test_container():
    container = _get_main_container().create_test_container()
    return DiTestContainer(container).initialize_container()


def _get_local_container():
    container = _get_main_container().create_test_container()
    return DiLocalContainer(container).initialize_container()


class DiContainer:
    def __init__(self):
        self.builder = ContainerBuilder()

    def initialize_container(self) -> Container:
        self.__init_orm_containers()
        self.__init_service_containers()
        self.__init_validators_containers()
        self.__init_permission_containers()
        self.__init_action_containers()
        self.container = self.builder.build()
        return self.container

    def __init_orm_containers(self):
        # обязательно синглтон, иначе пробьет лимит по подключениям
        self.builder.singleton(DatabaseConnection, DatabaseConnection)
        self.builder.register(Database, Database, scope=Scope.cached)
        self.builder.register(Transaction, Transaction)

        # users app
        self.builder.register(
            IProfileService, ORMProfileService, model=Profile
        )
        self.builder.register(
            IProfileTitleService, ORMProfileTitleService, model=BestPlayerTitle
        )
        self.builder.register(
            IStatisticService[Statistic],
            ORMStatisticService[Statistic],
            model=Statistic,
        )
        self.builder.register(
            IStatisticService[DayStatistic],
            ORMStatisticService[DayStatistic],
            model=DayStatistic,
        )
        self.builder.register(
            IStatisticService[MonthStatistic],
            ORMStatisticService[MonthStatistic],
            model=MonthStatistic,
        )
        self.builder.register(IUserService, ORMUserService, model=User)

        # game_settings app
        self.builder.register(
            IGameSettingsService, ORMGameSettingsService, model=GameSettings
        )

        # quiz app
        self.builder.register(
            IQuestionService, ORMQuestionsService, model=Question
        )
        self.builder.register(IAnswerService, ORMAnswerService, model=Answer)

        self.builder.register(
            IComplaintService, ORMComplaintService, model=Complaint
        )
        self.builder.register(
            ICategoryComplaintService,
            ORMCategoryComplaintService,
            model=CategoryComplaint,
        )

    def __init_service_containers(self):
        self.builder.singleton(
            "RedisTokenDBConnection",
            RedisPool,
            db_number=settings.redis_db_token,
        )

        self.builder.register(
            ITokenStorage,
            lambda: RedisTokenStorage(
                self.container.resolve(
                    "RedisTokenDBConnection",
                )
            ),
        )
        self.builder.register(BlacklistRefreshToken, BlacklistRefreshToken)

    def __init_validators_containers(self):
        self.builder.register(ProfileValidator, ProfileValidator)
        self.builder.register(DeviceTokenValidate, DeviceTokenValidate)
        self.builder.register(AnswerListValidator, AnswerListValidator)

    def __init_permission_containers(self):
        self.builder.register(ProfilePermissions, ProfilePermissions)
        self.builder.register(DevicePermissions, DevicePermissions)
        self.builder.register(IsAdminUser, IsAdminUser)

    def __init_action_containers(self):
        self.builder.register(ProfileActions, ProfileActions)
        self.builder.register(
            StatisticsActions[Statistic], StatisticsActions[Statistic]
        )
        self.builder.register(
            StatisticsActions[DayStatistic], StatisticsActions[DayStatistic]
        )
        self.builder.register(
            StatisticsActions[MonthStatistic],
            StatisticsActions[MonthStatistic],
        )

        def build_compose_actions(
            a: StatisticsActions[Statistic],
            b: StatisticsActions[DayStatistic],
            c: StatisticsActions[MonthStatistic],
        ):
            return [a, b, c]

        self.builder.register("list_statistic_actions", build_compose_actions)

        self.builder.register(
            CompositeStatisticAction,
            CompositeStatisticAction,
            actions=Dep("list_statistic_actions"),
            transaction=Dep(Transaction),
        )

        self.builder.register(QuestionsActions, QuestionsActions)
        self.builder.register(ComplaintsActions, ComplaintsActions)
        self.builder.register(
            CategoryComplaintsActions, CategoryComplaintsActions
        )
        self.builder.register(GameSettingsActions, GameSettingsActions)
        self.builder.register(AdminAuthAction, AdminAuthAction)


class DiLocalContainer:
    def __init__(self, container: TestContainer):
        self.container = container

    def initialize_container(self) -> TestContainer:
        self.container = self.container.with_overridden(
            ProfileValidator, ProfileValidatorLocal
        )
        return self.container


class DiTestContainer:
    def __init__(self, container: TestContainer):
        self.container = container

    def initialize_container(self) -> TestContainer:
        self.container = self.container.with_overridden(
            ProfileValidator, ProfileValidatorLocal
        )
        return self.container
