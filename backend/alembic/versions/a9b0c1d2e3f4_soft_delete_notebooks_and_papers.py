"""add soft delete is_active for notebooks and question papers

Revision ID: a9b0c1d2e3f4
Revises: f8a9b0c1d2e3
Create Date: 2026-07-30 19:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a9b0c1d2e3f4"
down_revision: str | Sequence[str] | None = "f8a9b0c1d2e3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "notebooks",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    op.drop_index("uq_notebooks_user_name_ci", table_name="notebooks")
    op.execute(
        """
        CREATE UNIQUE INDEX uq_notebooks_user_name_ci
        ON notebooks (user_id, lower(btrim(name)))
        WHERE is_active IS TRUE
        """
    )

    op.drop_index("ix_question_papers_notebook_updated", table_name="question_papers")
    op.execute(
        """
        CREATE INDEX ix_question_papers_notebook_updated
        ON question_papers (notebook_id, updated_at)
        WHERE is_active IS TRUE
        """
    )


def downgrade() -> None:
    op.drop_index("ix_question_papers_notebook_updated", table_name="question_papers")
    op.execute(
        """
        CREATE INDEX ix_question_papers_notebook_updated
        ON question_papers (notebook_id, updated_at)
        """
    )

    op.drop_index("uq_notebooks_user_name_ci", table_name="notebooks")
    op.execute(
        """
        CREATE UNIQUE INDEX uq_notebooks_user_name_ci
        ON notebooks (user_id, lower(btrim(name)))
        """
    )

    op.drop_column("question_papers", "is_active")
    op.drop_column("notebooks", "is_active")
