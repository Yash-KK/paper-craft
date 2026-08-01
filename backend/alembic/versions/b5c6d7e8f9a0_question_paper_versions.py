"""Split question_papers into parent + version tables.

Revision ID: b5c6d7e8f9a0
Revises: a4b5c6d7e8f9
Create Date: 2026-07-26 19:15:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5c6d7e8f9a0"
down_revision: str | Sequence[str] | None = "a4b5c6d7e8f9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "question_paper_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question_paper_id", sa.UUID(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
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
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("teacher_instructions", sa.Text(), nullable=True),
        sa.Column(
            "selected_chapters",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
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
        sa.Column(
            "selected_chat_messages",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "generation_context",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "generation_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("format_reference_uri", sa.String(length=1024), nullable=False),
        sa.Column(
            "format_reference_is_default",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("base_version_id", sa.UUID(), nullable=True),
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
            ["question_paper_id"], ["question_papers.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["base_version_id"],
            ["question_paper_versions.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "question_paper_id",
            "version_number",
            name="uq_question_paper_versions_paper_number",
        ),
    )
    op.create_index(
        "ix_question_paper_versions_paper_updated",
        "question_paper_versions",
        ["question_paper_id", "updated_at"],
        unique=False,
    )
    op.create_index(
        "ix_question_paper_versions_paper_status",
        "question_paper_versions",
        ["question_paper_id", "status"],
        unique=False,
    )

    # Backfill: each existing flat paper becomes Version 1 under the same parent id.
    op.execute(
        sa.text(
            """
            INSERT INTO question_paper_versions (
                id,
                question_paper_id,
                version_number,
                status,
                subject,
                grade,
                teacher_instructions,
                selected_chapters,
                blueprint,
                final_paper,
                final_answer_key,
                generated_items,
                selected_chat_messages,
                generation_context,
                generation_metadata,
                format_reference_uri,
                format_reference_is_default,
                base_version_id,
                error,
                created_at,
                updated_at
            )
            SELECT
                gen_random_uuid(),
                qp.id,
                1,
                qp.status,
                qp.subject,
                qp.grade,
                qp.teacher_instructions,
                COALESCE(qp.selected_chapters, '[]'::jsonb),
                COALESCE(qp.blueprint, '{}'::jsonb),
                COALESCE(qp.final_paper, '{}'::jsonb),
                COALESCE(qp.final_answer_key, '{}'::jsonb),
                COALESCE(qp.generated_items, '[]'::jsonb),
                '[]'::jsonb,
                '{}'::jsonb,
                '{}'::jsonb,
                qp.format_reference_uri,
                qp.format_reference_is_default,
                NULL,
                qp.error,
                qp.created_at,
                qp.updated_at
            FROM question_papers AS qp
            """
        )
    )

    op.drop_index("ix_question_papers_notebook_status", table_name="question_papers")
    op.drop_column("question_papers", "status")
    op.drop_column("question_papers", "version")
    op.drop_column("question_papers", "subject")
    op.drop_column("question_papers", "grade")
    op.drop_column("question_papers", "teacher_instructions")
    op.drop_column("question_papers", "selected_chapters")
    op.drop_column("question_papers", "blueprint")
    op.drop_column("question_papers", "final_paper")
    op.drop_column("question_papers", "final_answer_key")
    op.drop_column("question_papers", "generated_items")
    op.drop_column("question_papers", "format_reference_uri")
    op.drop_column("question_papers", "format_reference_is_default")
    op.drop_column("question_papers", "error")


def downgrade() -> None:
    op.add_column(
        "question_papers",
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
            server_default="pending",
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "question_papers",
        sa.Column("subject", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "question_papers",
        sa.Column("grade", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "question_papers",
        sa.Column("teacher_instructions", sa.Text(), nullable=True),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "selected_chapters",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "blueprint",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "final_paper",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "final_answer_key",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "generated_items",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "format_reference_uri",
            sa.String(length=1024),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "question_papers",
        sa.Column(
            "format_reference_is_default",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.add_column("question_papers", sa.Column("error", sa.Text(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE question_papers AS qp
            SET
                status = v.status,
                version = v.version_number,
                subject = v.subject,
                grade = v.grade,
                teacher_instructions = v.teacher_instructions,
                selected_chapters = v.selected_chapters,
                blueprint = v.blueprint,
                final_paper = v.final_paper,
                final_answer_key = v.final_answer_key,
                generated_items = v.generated_items,
                format_reference_uri = v.format_reference_uri,
                format_reference_is_default = v.format_reference_is_default,
                error = v.error
            FROM (
                SELECT DISTINCT ON (question_paper_id) *
                FROM question_paper_versions
                ORDER BY question_paper_id, version_number DESC
            ) AS v
            WHERE qp.id = v.question_paper_id
            """
        )
    )

    op.create_index(
        "ix_question_papers_notebook_status",
        "question_papers",
        ["notebook_id", "status"],
        unique=False,
    )
    op.drop_index(
        "ix_question_paper_versions_paper_status",
        table_name="question_paper_versions",
    )
    op.drop_index(
        "ix_question_paper_versions_paper_updated",
        table_name="question_paper_versions",
    )
    op.drop_table("question_paper_versions")
