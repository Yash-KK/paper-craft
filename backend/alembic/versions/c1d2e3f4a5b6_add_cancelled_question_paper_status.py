"""add cancelled status to question_paper_status

Revision ID: c1d2e3f4a5b6
Revises: b0c1d2e3f4a5
Create Date: 2026-08-01 19:05:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: str | Sequence[str] | None = "b0c1d2e3f4a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# status uses native_enum=False + create_constraint=True → VARCHAR CHECK, not PG ENUM.
_STATUS_CHECK = "question_paper_status"
_TABLE = "question_paper_versions"


def upgrade() -> None:
    op.drop_constraint(_STATUS_CHECK, _TABLE, type_="check")
    op.create_check_constraint(
        _STATUS_CHECK,
        _TABLE,
        "status IN ('pending', 'running', 'ready', 'failed', 'cancelled')",
    )


def downgrade() -> None:
    op.execute(
        f"UPDATE {_TABLE} SET status = 'failed' WHERE status = 'cancelled'"
    )
    op.drop_constraint(_STATUS_CHECK, _TABLE, type_="check")
    op.create_check_constraint(
        _STATUS_CHECK,
        _TABLE,
        "status IN ('pending', 'running', 'ready', 'failed')",
    )
