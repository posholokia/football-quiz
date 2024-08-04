from dataclasses import dataclass

from apps.users.actions.statistic import CompositeStatisticAction
from apps.users.models import ProfileEntity
from apps.users.services.storage import IProfileService
from apps.users.services.validator.profile import ProfileValidator


@dataclass
class ProfileActions:
    profile_repository: IProfileService
    statistic_repository: CompositeStatisticAction
    validator: ProfileValidator

    async def create(self, device_uuid: str) -> ProfileEntity:
        # создаем профиль
        profile = await self.profile_repository.create(device_uuid)
        profile_pk = profile.id

        name = f"Игрок-{profile_pk}"
        #  присваиваем профилю новое имя
        profile = await self.profile_repository.patch(profile_pk, name=name)

        # await self.statistic_repository.create(profile_pk)
        return profile

    async def get_by_id(self, pk: int) -> ProfileEntity:
        return await self.profile_repository.get_by_id(pk)

    async def get_by_device(self, device_uuid: str) -> ProfileEntity:
        return await self.profile_repository.get_by_device(device_uuid)

    async def patch_profile(self, pk: int, name: str) -> ProfileEntity:
        # await self.validator.validate(name=name)
        profile = await self.profile_repository.patch(pk, name=name)
        return profile
