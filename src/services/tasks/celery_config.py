from config import settings


broker_url = settings.broker_url
result_backend = settings.result_backend

accept_content = ["application/json"]
task_serializer = "json"
result_serializer = "json"
broker_connection_retry_on_startup = True
enable_utc = True
broker_connection_timeout = 2
broker_pool_limit = None
beat_dburi = str(settings.database_url) + "?async_fallback=True"
