from celery import Celery
from app.config import settings

celery_app = Celery(
    "pipeline_tasks",
    broker=settings.BROKER_URL,
    backend=settings.BROKER_URL
)

# Celery configuration
celery_app.conf.update(
    # Important: Tells Celery to import tasks from "app.tasks"
    imports=("app.tasks",),
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
