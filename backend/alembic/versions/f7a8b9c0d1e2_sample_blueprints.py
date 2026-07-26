"""sample_blueprints table + 40 Marks seed

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-07-26 10:15:00.000000

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "e6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sample_blueprints",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("total_marks", sa.Integer(), nullable=False),
        sa.Column("board", sa.String(length=20), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=100), nullable=True),
        sa.Column("blueprint", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_sample_blueprints_active_sort",
        "sample_blueprints",
        ["is_active", "sort_order"],
        unique=False,
    )

    from app.services.generation.sample_blueprints_data import FORTY_MARKS_BLUEPRINT

    op.bulk_insert(
        sa.table(
            "sample_blueprints",
            sa.column("id", sa.UUID()),
            sa.column("slug", sa.String()),
            sa.column("label", sa.String()),
            sa.column("total_marks", sa.Integer()),
            sa.column("board", sa.String()),
            sa.column("grade", sa.Integer()),
            sa.column("subject", sa.String()),
            sa.column("blueprint", postgresql.JSONB()),
            sa.column("sort_order", sa.Integer()),
            sa.column("is_active", sa.Boolean()),
        ),
        [
            {
                "id": uuid.uuid4(),
                "slug": "40-marks",
                "label": "40 Marks",
                "total_marks": 40,
                "board": "CBSE",
                "grade": 10,
                "subject": "Mathematics",
                "blueprint": FORTY_MARKS_BLUEPRINT,
                "sort_order": 40,
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_sample_blueprints_active_sort", table_name="sample_blueprints")
    op.drop_table("sample_blueprints")
