from config.config_builder import ConfigBuilder

from .base_settings.common import GlobalConf
from .base_settings.database import DatabaseConf
from .base_settings.firebase import FirebaseConf
from .base_settings.rabbitmq import RabbitMQConf
from .base_settings.redis import RedisConf


class Settings(
    GlobalConf,
    DatabaseConf,
    RedisConf,
    RabbitMQConf,
    FirebaseConf,
):
    pass


settings = ConfigBuilder.build_from_env(Settings)
