from config.config_builder import ConfigBuilder

from .base_settings.common import GlobalConf
from .base_settings.database import DatabaseConf
from .base_settings.redis import RedisConf


class Settings(
    GlobalConf,
    DatabaseConf,
    RedisConf,
):
    pass


settings = ConfigBuilder.build_from_env(Settings)
