"""fix sample_blueprint enum storage to match app convention

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
Create Date: 2026-07-26 12:40:00.000000

Stores Board/Subject/ClassGrade as enum *names* (CLASS_10, MATHEMATICS),
matching notebooks and chapter_catalog.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c0d1e2f3a4b5"
down_revision: str | Sequence[str] | None = "b9c0d1e2f3a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET grade = CASE
                    WHEN grade IN ('10', 'Class 10', 'CLASS_10') THEN 'CLASS_10'
                    WHEN grade IN ('9', 'Class 9', 'CLASS_9') THEN 'CLASS_9'
                    ELSE grade
                END,
                subject = CASE
                    WHEN subject IN ('Mathematics', 'MATHEMATICS') THEN 'MATHEMATICS'
                    ELSE subject
                END,
                updated_at = now()
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET grade = CASE
                    WHEN grade = 'CLASS_10' THEN 'Class 10'
                    WHEN grade = 'CLASS_9' THEN 'Class 9'
                    ELSE grade
                END,
                subject = CASE
                    WHEN subject = 'MATHEMATICS' THEN 'Mathematics'
                    ELSE subject
                END,
                updated_at = now()
            """
        )
    )
