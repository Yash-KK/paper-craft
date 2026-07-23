"""add board to catalog, notebooks, and profiles

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-07-23 22:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, Sequence[str], None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chapter_catalog",
        sa.Column(
            "board",
            sa.String(length=20),
            nullable=False,
            server_default="CBSE",
        ),
    )
    op.drop_constraint(
        "uq_chapter_catalog_book_chapter",
        "chapter_catalog",
        type_="unique",
    )
    op.drop_index("ix_chapter_catalog_grade_subject", table_name="chapter_catalog")
    op.create_unique_constraint(
        "uq_chapter_catalog_board_book_chapter",
        "chapter_catalog",
        ["board", "book_code", "chapter_number"],
    )
    op.create_index(
        "ix_chapter_catalog_board_grade_subject",
        "chapter_catalog",
        ["board", "grade", "subject"],
    )
    op.alter_column("chapter_catalog", "board", server_default=None)

    op.add_column(
        "notebooks",
        sa.Column(
            "board",
            sa.String(length=20),
            nullable=True,
            server_default="CBSE",
        ),
    )
    op.execute(sa.text("UPDATE notebooks SET board = 'CBSE' WHERE board IS NULL"))
    op.alter_column("notebooks", "board", server_default=None)

    op.add_column(
        "user_profiles",
        sa.Column("board", sa.String(length=20), nullable=True),
    )
    op.execute(sa.text("UPDATE user_profiles SET board = 'CBSE' WHERE board IS NULL"))


def downgrade() -> None:
    op.drop_column("user_profiles", "board")
    op.drop_column("notebooks", "board")

    op.drop_index(
        "ix_chapter_catalog_board_grade_subject",
        table_name="chapter_catalog",
    )
    op.drop_constraint(
        "uq_chapter_catalog_board_book_chapter",
        "chapter_catalog",
        type_="unique",
    )
    op.create_index(
        "ix_chapter_catalog_grade_subject",
        "chapter_catalog",
        ["grade", "subject"],
    )
    op.create_unique_constraint(
        "uq_chapter_catalog_book_chapter",
        "chapter_catalog",
        ["book_code", "chapter_number"],
    )
    op.drop_column("chapter_catalog", "board")
