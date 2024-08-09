from sqlalchemy import inspect
from sqlalchemy.orm.base import LoaderCallableStatus as load_status

from apps.users.models import StatisticEntity


class StatisticToEntityMixin:
    def to_entity(self) -> StatisticEntity:
        """
        Преобразует ORM в объект Entity.
        Если связанный объект(ы) не подгружен из БД,
        то в поле объекта будет None или пустой список соответственно
        """
        profile = (
            self.profile.to_entity()
            if not inspect(self).attrs.profile.loaded_value
            == load_status.NO_VALUE
            else None
        )
        return StatisticEntity(
            id=self.id,
            games=self.games,
            score=self.score,
            place=self.place,
            rights=self.rights,
            wrongs=self.wrongs,
            trend=self.trend,
            perfect_rounds=self.perfect_rounds,
            profile=profile,
        )
