from sqlalchemy import (
    Float,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from apps.game_settings.models import GameSettingsEntity
from core.database.db import Base


class GameSettings(Base):
    __tablename__ = "game_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    time_round: Mapped[int] = mapped_column(
        Integer,
        doc="Время раунда, секунды",
        nullable=False,
    )
    question_limit: Mapped[int] = mapped_column(
        Integer,
        doc="Количество вопросов в раунде",
        nullable=False,
    )
    max_energy: Mapped[int] = mapped_column(
        Integer,
        doc="Максимальная энергия",
        nullable=False,
    )
    start_energy: Mapped[int] = mapped_column(
        Integer,
        doc="Стартовая энергия",
        nullable=False,
    )
    energy_for_ad: Mapped[int] = mapped_column(
        Integer,
        doc="Количество энергии за рекламу",
        nullable=False,
    )
    round_cost: Mapped[int] = mapped_column(
        Integer,
        doc="Стоимость раунда, энергия",
        nullable=False,
    )
    question_skip_cost: Mapped[int] = mapped_column(
        Integer,
        doc="Стоимость пропуска вопроса, энергия",
        nullable=False,
    )
    energy_perfect_round: Mapped[int] = mapped_column(
        Integer,
        doc="Энергия за раунд без ошибок",
        nullable=False,
    )
    recovery_period: Mapped[int] = mapped_column(
        Integer,
        doc="Частота восстановления энергии, сек",
        nullable=False,
    )
    recovery_value: Mapped[int] = mapped_column(
        Integer,
        doc="По сколько энергии восстанавливается со временем",
        nullable=False,
    )
    right_ratio: Mapped[float] = mapped_column(
        Float,
        doc="Коэффициент за верные ответы",
        nullable=False,
    )
    wrong_ratio: Mapped[float] = mapped_column(
        Float,
        doc="Коэффициент за неверные ответы",
        nullable=False,
    )

    def to_entity(self) -> GameSettingsEntity:
        """
        Преобразует ORM в объект Entity.
        Если связанный объект(ы) не подгружен из БД,
        то в поле объекта будет None или пустой список соответственно
        """
        return GameSettingsEntity(
            id=self.id,
            time_round=self.time_round,
            question_limit=self.question_limit,
            max_energy=self.max_energy,
            start_energy=self.start_energy,
            energy_for_ad=self.energy_for_ad,
            round_cost=self.round_cost,
            question_skip_cost=self.question_skip_cost,
            energy_perfect_round=self.energy_perfect_round,
            recovery_period=self.recovery_period,
            recovery_value=self.recovery_value,
            right_ratio=self.right_ratio,
            wrong_ratio=self.wrong_ratio,
        )
