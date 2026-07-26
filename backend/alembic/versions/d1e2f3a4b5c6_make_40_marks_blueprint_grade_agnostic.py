"""make 40 Marks blueprint grade agnostic

Revision ID: d1e2f3a4b5c6
Revises: c0d1e2f3a4b5
Create Date: 2026-07-26 13:54:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: str | Sequence[str] | None = "c0d1e2f3a4b5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET grade = NULL,
                updated_at = now()
            WHERE slug = '40-marks'
              AND board = 'CBSE'
              AND subject = 'MATHEMATICS'
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET grade = 'CLASS_10',
                updated_at = now()
            WHERE slug = '40-marks'
              AND board = 'CBSE'
              AND subject = 'MATHEMATICS'
            """
        )
    )
