from dataclasses import dataclass

from apps.users.exceptions.profile import DoesNotExistsProfile
from apps.users.models import ProfileEntity
from apps.users.services.storage import IProfileService
from apps.users.validator.profile import ProfileValidator


@dataclass
class ProfileActions:
    __profile_repository: IProfileService
    validator: ProfileValidator

    async def create(self, device_uuid: str) -> ProfileEntity:
        """
        Создание профиля игрока.

        :param device_uuid: Уникальный идентификатор устройства.
        :return:            Профиль.
        """
        # создаем профиль
        profile = await self.__profile_repository.create(
            name="Игрок", device_uuid=device_uuid
        )
        profile_pk = profile.id

        name = f"Игрок-{profile_pk}"
        #  присваиваем профилю новое имя
        return await self.__profile_repository.update(profile_pk, name=name)

    async def get_profile(self, **filter_by) -> ProfileEntity:
        """
        Получить профиль игрока.

        :param filter_by:   Данные для фильтрации (поиска) профиля.
                            id - уникально;
                            device_uuid - уникально;
                            user_id - уникально;
                            name.
        :return:            Профиль.
        """
        profile = await self.__profile_repository.get_one(**filter_by)
        if profile is None:
            raise DoesNotExistsProfile(
                detail=f"Профиль по параметрам {filter_by} не найден"
            )
        return profile

    async def patch_profile(self, pk: int, **fields) -> ProfileEntity:
        """
        Обновление профиля игрока.

        :param pk:      Id профиля.
        :param fields:  Аргументы для обновления профиля. Возможно обновить:
                        name, last_visit.
        :return:        Профиль.
        """
        await self.validator.validate(name=fields.get("name"))
        return await self.__profile_repository.update(pk, **fields)

    async def get_list_admin(
        self,
        page: int,
        limit: int,
        search: str,
    ) -> list[tuple[ProfileEntity, int]]:
        """
        Получить список профилей с количеством оставленных жалоб.
        Метод используется в админ панели.

        :param page:    Номер страницы, с которой получить данные.
        :param limit:   Количество записей на странице.
        :param search:  Поиск по имени профиля.
        :retutn:        Список из кортежей Профиль + число жалоб.
        """
        offset = (page - 1) * limit
        profiles = (
            await self.__profile_repository.get_list_with_complaints_count(
                offset, limit, search
            )
        )
        return [(profile, complaints) for profile, complaints in profiles]

    async def get_count(self, search: str | None = None) -> int:
        """
        Возвращает общее число профилей соответсвующих условию фильтрации.

        :param search:  Условие поиска профилей, поиск ведется по имени.
        :return:        Кол-во профилей.
        """
        return await self.__profile_repository.get_count(search)

    async def reset_name(self, pk: int) -> tuple[ProfileEntity, int]:
        """
        Сброс имени профиля к значению по-умолчанию.

        :param pk:  ID профиля.
        :return:    Кортеж из профиля и числа жалоб.
        """
        await self.__profile_repository.update(pk, name=f"Игрок-{pk}")
        (
            profile,
            complaints,
        ) = await self.__profile_repository.get_with_complaints_count_by_id(pk)
        return profile, complaints
