from dataclasses import dataclass

from core.apps.users.actions import (
    ProfileActions,
    StatisticsActions,
)
from core.apps.users.schema import SetStatisticsSchema


@dataclass
class CompositeStatisticAction:
    actions: list[StatisticsActions]

    async def patch(
        self,
        profile_pk: int,
        game_stat: SetStatisticsSchema,
    ) -> None:
        for action in self.actions:
            await action.patch(profile_pk, game_stat)


@dataclass
class CompositeProfileAction:
    actions: list[ProfileActions]

    async def create(self, device_uuid: str) -> None:
        for action in self.actions:
            await action.create(device_uuid)
