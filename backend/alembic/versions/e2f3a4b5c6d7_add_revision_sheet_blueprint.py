"""add Revision Sheet sample blueprint + flexible kinds

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-07-26 14:05:00.000000

"""

from __future__ import annotations

import json
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e2f3a4b5c6d7"
down_revision: str | Sequence[str] | None = "d1e2f3a4b5c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

REVISION_SHEET_FORMAT_URI = "local:samples/revision_sheet.docx"


def upgrade() -> None:
    from app.services.generation.sample_blueprints_data import (
        FORTY_MARKS_BLUEPRINT,
        REVISION_SHEET_BLUEPRINT,
    )

    op.add_column(
        "sample_blueprints",
        sa.Column(
            "kind",
            sa.String(length=40),
            nullable=False,
            server_default="EXAM",
        ),
    )
    op.alter_column(
        "sample_blueprints",
        "total_marks",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET kind = 'EXAM',
                total_marks = 40,
                blueprint = CAST(:blueprint AS jsonb),
                updated_at = now()
            WHERE slug = '40-marks'
            """
        ).bindparams(blueprint=json.dumps(FORTY_MARKS_BLUEPRINT))
    )

    sample_blueprints = sa.table(
        "sample_blueprints",
        sa.column("id", sa.UUID()),
        sa.column("slug", sa.String()),
        sa.column("label", sa.String()),
        sa.column("kind", sa.String()),
        sa.column("total_marks", sa.Integer()),
        sa.column("board", sa.String()),
        sa.column("grade", sa.String()),
        sa.column("subject", sa.String()),
        sa.column("format_reference_uri", sa.String()),
        sa.column("blueprint", postgresql.JSONB()),
        sa.column("sort_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        sample_blueprints,
        [
            {
                "id": uuid.uuid4(),
                "slug": "revision-sheet",
                "label": "Revision Sheet",
                "kind": "REVISION_SHEET",
                "total_marks": None,
                "board": "CBSE",
                "grade": None,
                "subject": "MATHEMATICS",
                "format_reference_uri": REVISION_SHEET_FORMAT_URI,
                "blueprint": REVISION_SHEET_BLUEPRINT,
                "sort_order": 50,
                "is_active": True,
            }
        ],
    )

    op.alter_column(
        "sample_blueprints",
        "kind",
        server_default=None,
        existing_type=sa.String(length=40),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM sample_blueprints WHERE slug = 'revision-sheet'")
    )
    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET total_marks = COALESCE(total_marks, 40)
            WHERE slug = '40-marks'
            """
        )
    )
    op.alter_column(
        "sample_blueprints",
        "total_marks",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("sample_blueprints", "kind")
