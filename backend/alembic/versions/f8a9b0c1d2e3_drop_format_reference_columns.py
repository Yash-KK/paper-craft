"""drop format reference columns

Revision ID: f8a9b0c1d2e3
Revises: c6d7e8f9a0b1
Create Date: 2026-07-30 11:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f8a9b0c1d2e3"
down_revision: Union[str, Sequence[str], None] = "c6d7e8f9a0b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("question_paper_versions", "format_reference_is_default")
    op.drop_column("question_paper_versions", "format_reference_uri")
    op.drop_column("sample_blueprints", "format_reference_uri")


def downgrade() -> None:
    op.add_column(
        "sample_blueprints",
        sa.Column("format_reference_uri", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "question_paper_versions",
        sa.Column(
            "format_reference_uri",
            sa.String(length=1024),
            nullable=False,
            server_default="local:samples/40_marks_sample.docx",
        ),
    )
    op.add_column(
        "question_paper_versions",
        sa.Column(
            "format_reference_is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.alter_column(
        "question_paper_versions",
        "format_reference_uri",
        server_default=None,
    )
