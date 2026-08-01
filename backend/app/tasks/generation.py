"""Celery tasks for question-paper generation."""

from __future__ import annotations

import logging
from uuid import UUID

from app.core.celery_app import celery_app
from app.services.generation.next_version import run_next_version_generation
from app.services.generation.papers import fail_stuck_versions, run_paper_generation

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.generation.generate_question_paper",
    bind=True,
    max_retries=0,
)
def generate_question_paper_task(self, version_id: str) -> dict[str, str]:
    """Background job: generate Version 1 of a question paper from scratch."""
    del self
    version_uuid = UUID(version_id)
    logger.info("Starting generation task version_id=%s", version_uuid)
    run_paper_generation(version_uuid)
    return {"version_id": version_id, "status": "done"}


@celery_app.task(
    name="app.tasks.generation.generate_next_question_paper_version",
    bind=True,
    max_retries=0,
)
def generate_next_question_paper_version_task(self, version_id: str) -> dict[str, str]:
    """Background job: generate the next version from a prior ready version."""
    del self
    version_uuid = UUID(version_id)
    logger.info("Starting next-version generation task version_id=%s", version_uuid)
    run_next_version_generation(version_uuid)
    return {"version_id": version_id, "status": "done"}


@celery_app.task(name="app.tasks.generation.fail_stuck_question_papers")
def fail_stuck_question_papers() -> dict[str, int]:
    """Periodic Beat job: fail versions stuck in running too long."""
    count = fail_stuck_versions()
    return {"failed_count": count}
