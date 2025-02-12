from celery import Celery
from app.config import settings

# Initialize a Celery application with a name and broker/backend URLs
celery_app = Celery(
    "pipeline_tasks",  # Name of the Celery application
    broker=settings.BROKER_URL,  # URL for the message broker (Redis)
    backend=settings.BROKER_URL  # URL for the result backend (Redis)
)

# Celery configuration
celery_app.conf.update(
    imports=("app.tasks",),  # Import tasks from the specified module
    result_expires=3600,  # Time in seconds before task results expire
    task_serializer='json',  # Format for serializing task data
    accept_content=['json'],  # Accepted content types for tasks
    result_serializer='json',  # Format for serializing task results
    timezone='UTC',  # Timezone for the Celery application
    enable_utc=True,  # Enable UTC for task scheduling
)
