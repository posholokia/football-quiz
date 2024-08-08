from dataclasses import dataclass

from apps.users.actions.statistic import CompositeStatisticAction
from apps.users.models import (
    ProfileAdminDTO,
    ProfileEntity,
)
from apps.users.services.storage import IProfileService
from apps.users.validator.profile import ProfileValidator


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

    async def patch_profile(self, pk: int, **fields) -> ProfileEntity:
        await self.validator.validate(name=fields.get("name"))
        return await self.profile_repository.patch(pk, **fields)

    async def get_list(
        self,
        page: int,
        limit: int,
        search: str,
    ) -> list[ProfileAdminDTO]:
        offset = (page - 1) * limit
        return await self.profile_repository.get_list_with_complaints_count(
            offset, limit, search
        )

    async def get_count(self, search: str | None = None) -> int:
        return await self.profile_repository.get_count(search)

    async def reset_name(self, pk: int) -> ProfileAdminDTO:
        await self.profile_repository.patch(pk, name=f"Игрок-{pk}")
        return await self.profile_repository.get_with_complaints_count_by_id(
            pk,
        )
