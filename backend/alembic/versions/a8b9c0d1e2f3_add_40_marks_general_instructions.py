"""add 40 Marks blueprint general instructions

Revision ID: a8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-07-26 11:40:00.000000

"""

import json
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8b9c0d1e2f3"
down_revision: str | Sequence[str] | None = "f7a8b9c0d1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    from app.services.generation.sample_blueprints_data import FORTY_MARKS_BLUEPRINT

    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET blueprint = CAST(:blueprint AS jsonb),
                updated_at = now()
            WHERE slug = '40-marks'
            """
        ).bindparams(blueprint=json.dumps(FORTY_MARKS_BLUEPRINT))
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET blueprint = jsonb_set(
                    blueprint,
                    '{general_instructions}',
                    '[]'::jsonb,
                    true
                ),
                updated_at = now()
            WHERE slug = '40-marks'
            """
        )
    )
