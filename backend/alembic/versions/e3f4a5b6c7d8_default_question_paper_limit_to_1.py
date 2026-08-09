"""default question_paper_limit to 1

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-08-09 13:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e3f4a5b6c7d8"
down_revision: str | Sequence[str] | None = "d2e3f4a5b6c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "question_paper_limit",
        existing_type=sa.Integer(),
        server_default="1",
        existing_nullable=False,
    )
    # Align existing accounts with the new default product quota.
    op.execute("UPDATE users SET question_paper_limit = 1")


def downgrade() -> None:
    op.alter_column(
        "users",
        "question_paper_limit",
        existing_type=sa.Integer(),
        server_default="2",
        existing_nullable=False,
    )
    op.execute("UPDATE users SET question_paper_limit = 2")
