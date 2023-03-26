import datetime
import celery
from celery import Celery
import redis
from celery.schedules import crontab
from src.core.settings import settings

celery_app = Celery('celery_main', broker=settings.REDIS_URL, include=["src.tasks"])
# celery --app celery_ worker --loglevel=info -Q remote_queue -n name

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

