import os
from celery import Celery

broker = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

app = Celery(
    "data_processor",
    broker=broker,
    backend=broker,
    include=["backend.tasks"]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
