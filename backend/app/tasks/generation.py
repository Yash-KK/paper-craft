"""Celery tasks for question-paper generation."""

from __future__ import annotations

import logging
from uuid import UUID

from app.core.celery_app import celery_app
from app.services.generation.papers import fail_stuck_versions, run_paper_generation

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.generation.generate_question_paper",
    bind=True,
    max_retries=0,
)
def generate_question_paper_task(self, version_id: str) -> dict[str, str]:
    """Background job: generate a question paper version by id."""
    del self
    version_uuid = UUID(version_id)
    logger.info("Starting generation task version_id=%s", version_uuid)
    run_paper_generation(version_uuid)
    return {"version_id": version_id, "status": "done"}


@celery_app.task(name="app.tasks.generation.fail_stuck_question_papers")
def fail_stuck_question_papers() -> dict[str, int]:
    """Periodic Beat job: fail versions stuck in running too long."""
    count = fail_stuck_versions()
    return {"failed_count": count}
