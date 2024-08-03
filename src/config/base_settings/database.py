from pydantic_settings import BaseSettings


class DatabaseConf(BaseSettings):
    db_schema: str
    db_user: str
    db_pass: str
    db_host: str
    db_name: str
    db_port: int

    @property
    def database_url(self):
        return (
            f"{self.db_schema}://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
