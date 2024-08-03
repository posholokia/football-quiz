from sqlalchemy import (
    Column,
    Float,
    Integer,
)

from core.database.db import Base


class GameSettings(Base):
    __tablename__ = "game_settings"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
    )
    time_round = Column(
        Integer,
        doc="Время раунда, секунды",
        nullable=False,
    )
    question_limit = Column(
        Integer,
        doc="Количество вопросов в раунде",
        nullable=False,
    )
    max_energy = Column(
        Integer,
        doc="Максимальная энергия",
        nullable=False,
    )
    start_energy = Column(
        Integer,
        doc="Стартовая энергия",
        nullable=False,
    )
    energy_for_ad = Column(
        Integer,
        doc="Количество энергии за рекламу",
        nullable=False,
    )
    round_cost = Column(
        Integer,
        doc="Стоимость раунда, энергия",
        nullable=False,
    )
    question_skip_cost = Column(
        Integer,
        doc="Стоимость пропуска вопроса, энергия",
        nullable=False,
    )
    energy_perfect_round = Column(
        Integer,
        doc="Энергия за раунд без ошибок",
        nullable=False,
    )
    recovery_period = Column(
        Integer,
        doc="Частота восстановления энергии, сек",
        nullable=False,
    )
    recovery_value = Column(
        Integer,
        doc="По сколько энергии восстанавливается со временем",
        nullable=False,
    )
    right_ratio = Column(
        Float,
        doc="Коэффициент за верные ответы",
        nullable=False,
    )
    wrong_ratio = Column(
        Float,
        doc="Коэффициент за неверные ответы",
        nullable=False,
    )
