"""question_papers table

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-07-26 18:55:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f3a4b5c6d7e8"
down_revision: str | Sequence[str] | None = "e2f3a4b5c6d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "question_papers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("notebook_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "ready",
                "failed",
                name="question_paper_status",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("teacher_instructions", sa.Text(), nullable=True),
        sa.Column(
            "blueprint",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "final_paper",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "final_answer_key",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "generated_items",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("format_reference_uri", sa.String(length=1024), nullable=False),
        sa.Column(
            "format_reference_is_default",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["notebook_id"], ["notebooks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_question_papers_notebook_updated",
        "question_papers",
        ["notebook_id", "updated_at"],
        unique=False,
    )
    op.create_index(
        "ix_question_papers_notebook_status",
        "question_papers",
        ["notebook_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_question_papers_notebook_status", table_name="question_papers"
    )
    op.drop_index(
        "ix_question_papers_notebook_updated", table_name="question_papers"
    )
    op.drop_table("question_papers")
