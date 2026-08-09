"""add per-account usage limits on users

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-08-09 12:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d2e3f4a5b6c7"
down_revision: str | Sequence[str] | None = "c1d2e3f4a5b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "question_paper_limit",
            sa.Integer(),
            server_default="2",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "question_paper_usage",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "version_limit",
            sa.Integer(),
            server_default="2",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "chat_message_limit",
            sa.Integer(),
            server_default="5",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "chat_message_usage",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )

    # Backfill lifetime usage from historical rows (including soft-deleted papers).
    op.execute(
        """
        UPDATE users AS u
        SET question_paper_usage = COALESCE((
            SELECT COUNT(*)::int
            FROM question_papers AS qp
            JOIN notebooks AS n ON n.id = qp.notebook_id
            WHERE n.user_id = u.id
        ), 0)
        """
    )
    op.execute(
        """
        UPDATE users AS u
        SET chat_message_usage = COALESCE((
            SELECT COUNT(*)::int
            FROM chat_messages AS cm
            JOIN chat_sessions AS cs ON cs.id = cm.session_id
            JOIN notebooks AS n ON n.id = cs.notebook_id
            WHERE n.user_id = u.id AND cm.role = 'user'
        ), 0)
        """
    )


def downgrade() -> None:
    op.drop_column("users", "chat_message_usage")
    op.drop_column("users", "chat_message_limit")
    op.drop_column("users", "version_limit")
    op.drop_column("users", "question_paper_usage")
    op.drop_column("users", "question_paper_limit")
