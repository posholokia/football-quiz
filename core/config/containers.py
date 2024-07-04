from functools import lru_cache

import punq

from sqlalchemy.ext.asyncio import AsyncSession

from core.apps.game_settings.actions.actions import GameSettingsActions
from core.apps.game_settings.services.storage.base import IGameSettingsService
from core.apps.game_settings.services.storage.sqla import ORMGameSettingsService
from core.apps.quiz.actions.actions import (
    ComplaintsActions,
    QuestionsActions, CategoryComplaintsActions,
)
from core.apps.quiz.permissions.quiz import DevicePermissions
from core.apps.quiz.services.storage.base import (
    IComplaintService,
    IQuestionService, ICategoryComplaintService,
)
from core.apps.quiz.services.storage.sqla import (
    ORMComplaintService,
    ORMQuestionsService, ORMCategoryComplaintService,
)
from core.apps.users.actions.actions import (
    ProfileActions,
    StatisticsActions,
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
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    container.register(AsyncSession, factory=lambda: SessionLocal())
    # orm интерфейсы
    container.register(IProfileService, ORMProfileService)
    container.register(IStatisticService, ORMStatisticService)
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
    container.register(ProfileActions)
    container.register(StatisticsActions)
    container.register(QuestionsActions)
    container.register(GameSettingsActions)
    container.register(ComplaintsActions)
    container.register(CategoryComplaintsActions)
    return container
