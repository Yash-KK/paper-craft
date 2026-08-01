"""chapter catalog is_available

Revision ID: d5e6f7a8b9c0
Revises: c4bd2c3bd230
Create Date: 2026-07-21 11:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5e6f7a8b9c0"
down_revision: str | Sequence[str] | None = "c4bd2c3bd230"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add is_available flag to chapter_catalog."""
    op.add_column(
        "chapter_catalog",
        sa.Column(
            "is_available",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE chapter_catalog
            SET is_available = true
            WHERE book_code = 'jemh1'
              AND chapter_number IN (1, 2)
            """
        )
    )


def downgrade() -> None:
    """Remove is_available flag from chapter_catalog."""
    op.drop_column("chapter_catalog", "is_available")
