from pathlib import Path

from celery import (
    bootsteps,
    Celery,
)
from celery.schedules import crontab
from celery.signals import after_task_publish


"""------------------------------------------------------------------"""
"""-------------ПРОБЫ ПРОВЕРКИ ЦЕЛОСТНОСТИ CELERY WORKER-------------"""
"""------------------------------------------------------------------"""

HEARTBEAT_FILE = Path("/tmp/celery_heartbeat")
READINESS_FILE = Path("/tmp/celery_ready")


# пробы готовности для celery-worker
class LivenessProbe(bootsteps.StartStopStep):
    requires = {"celery.worker.components:Timer"}

    def __init__(self, worker, **kwargs):
        self.requests = []
        self.tref = None

    def start(self, worker):
        self.tref = worker.timer.call_repeatedly(
            1.0,
            self.update_heartbeat_file,
            (worker,),
            priority=10,
        )

    def stop(self, worker):
        HEARTBEAT_FILE.unlink(missing_ok=True)

    def update_heartbeat_file(self, worker):
        HEARTBEAT_FILE.touch()


"""------------------------------------------------------------------"""
"""--------------------НАСТРОЙКИ ПРИЛОЖЕНИЯ CELERY-------------------"""
"""------------------------------------------------------------------"""


app = Celery("quiz")
app.steps["worker"].add(LivenessProbe)

app.config_from_object("services.tasks.celery_config")

app.autodiscover_tasks(packages=["services.tasks"])


"""------------------------------------------------------------------"""
"""--------------ПРОБЫ ПРОВЕРКИ ЦЕЛОСТНОСТИ CELERY BEAT--------------"""
"""------------------------------------------------------------------"""


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        60.0, celery_heartbeat.s(), name="celery_heartbeat"
    )


@app.task
def celery_heartbeat():
    pass  # важен запуск задачи, ей не нужно ничего делать.


@after_task_publish.connect(
    sender="services.tasks.celery_app.celery_heartbeat"
)
def task_published(**_):
    HEARTBEAT_FILE.touch()


"""------------------------------------------------------------------"""
"""-----------------------ПЕРИОДИЧЕСКИЕ ТАСКИ------------------------"""
"""------------------------------------------------------------------"""


app.conf.beat_schedule = {
    "clear_day_statistic": {
        "task": "clear_day_statistic",
        "schedule": crontab(minute="56", hour="12"),
    },
    "clear_month_statistic": {
        "task": "clear_month_statistic",
        "schedule": crontab(minute="56", hour="12", day_of_month="22"),
    },
    "update_firebase_config": {
        "task": "update_firebase_config",
        "schedule": crontab(minute="0", hour="0"),
    },
}
