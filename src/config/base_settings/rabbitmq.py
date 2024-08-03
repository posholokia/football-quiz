from pydantic_settings import BaseSettings


class RabbitMQConf(BaseSettings):
    rabbit_user: str
    rabbit_pass: str
    rabbit_host: str
    rabbit_vhost: str
    rabbit_port: int

    @property
    def broker_url(self):
        return (
            f"amqp://{self.rabbit_user}:{self.rabbit_pass}"
            f"@{self.rabbit_host}:{self.rabbit_port}/{self.rabbit_vhost}"
        )

    @property
    def result_backend(self):
        return (
            f"amqp://{self.rabbit_user}:{self.rabbit_pass}"
            f"@{self.rabbit_host}:{self.rabbit_port}/{self.rabbit_vhost}"
        )
