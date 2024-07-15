import os

from dotenv import load_dotenv

from core.config import settings


load_dotenv()


RABBIT_USER = os.getenv("RABBIT_USER")
RABBIT_PASS = os.getenv("RABBIT_PASS")
RABBIT_PORT = os.getenv("RABBIT_PORT")
RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_VHOST = os.getenv("RABBIT_VHOST")

broker_url = (
    f"amqp://{RABBIT_USER}:{RABBIT_PASS}"
    f"@{RABBIT_HOST}:{RABBIT_PORT}/{RABBIT_VHOST}"
)
result_backend = (
    f"rpc://{RABBIT_USER}:{RABBIT_PASS}"
    f"@{RABBIT_HOST}:{RABBIT_PORT}/{RABBIT_VHOST}"
)
accept_content = ["application/json"]
task_serializer = "json"
result_serializer = "json"
broker_connection_retry_on_startup = True
enable_utc = True
broker_connection_timeout = 2
broker_pool_limit = None
beat_dburi = str(settings.DATABASE_URL) + "?async_fallback=True"
