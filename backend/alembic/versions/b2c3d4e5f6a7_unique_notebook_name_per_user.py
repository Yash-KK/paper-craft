"""unique notebook name per user

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-17 16:40:00.000000

"""

from collections.abc import Sequence

from alembic import op


revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX uq_notebooks_user_name_ci
        ON notebooks (user_id, lower(btrim(name)))
        """
    )


def downgrade() -> None:
    op.drop_index("uq_notebooks_user_name_ci", table_name="notebooks")
