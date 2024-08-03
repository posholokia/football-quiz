from pydantic_settings import BaseSettings


class GlobalConf(BaseSettings):
    debug: bool = False
    crypto_key: str
    environ: str
