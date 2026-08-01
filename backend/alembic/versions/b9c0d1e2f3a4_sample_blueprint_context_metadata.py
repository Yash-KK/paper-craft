"""align sample_blueprint metadata with board/subject/grade enums

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
Create Date: 2026-07-26 12:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b9c0d1e2f3a4"
down_revision: str | Sequence[str] | None = "a8b9c0d1e2f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FORTY_MARKS_FORMAT_URI = "local:samples/40_marks_sample.docx"


def upgrade() -> None:
    op.add_column(
        "sample_blueprints",
        sa.Column("format_reference_uri", sa.String(length=512), nullable=True),
    )

    # Integer grade (10) → ClassGrade label ("Class 10").
    op.execute(
        sa.text(
            """
            ALTER TABLE sample_blueprints
            ALTER COLUMN grade TYPE VARCHAR(50)
            USING CASE
                WHEN grade::text IN ('9', 'Class 9', 'CLASS_9') THEN 'CLASS_9'
                WHEN grade::text IN ('10', 'Class 10', 'CLASS_10') THEN 'CLASS_10'
                ELSE grade::text
            END
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET format_reference_uri = :uri,
                board = COALESCE(board, 'CBSE'),
                subject = 'MATHEMATICS',
                grade = 'CLASS_10',
                updated_at = now()
            WHERE slug = '40-marks'
            """
        ).bindparams(uri=FORTY_MARKS_FORMAT_URI)
    )

    op.create_index(
        "ix_sample_blueprints_active_board_subject",
        "sample_blueprints",
        ["is_active", "board", "subject", "sort_order"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sample_blueprints_active_board_subject",
        table_name="sample_blueprints",
    )
    op.drop_column("sample_blueprints", "format_reference_uri")

    op.execute(
        sa.text(
            """
            ALTER TABLE sample_blueprints
            ALTER COLUMN grade TYPE INTEGER
            USING CASE
                WHEN grade = 'Class 9' THEN 9
                WHEN grade = 'Class 10' THEN 10
                WHEN grade ~ '^[0-9]+$' THEN grade::integer
                ELSE NULL
            END
            """
        )
    )
