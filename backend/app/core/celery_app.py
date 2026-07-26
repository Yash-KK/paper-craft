"""Celery application for PaperCraft background jobs."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "paper_craft",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.generation"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "fail-stuck-question-papers": {
            "task": "app.tasks.generation.fail_stuck_question_papers",
            "schedule": 300.0,  # every 5 minutes
        },
    },
)
