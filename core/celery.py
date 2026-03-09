import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app: Celery = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(broker_connection_retry_on_startup=True)

app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    "fetch-currency-stats-every-minute": {
        "task": "currency_app.tasks.get_currency_rates",
        "schedule": crontab(minute="*/1"),
    },
}
