"""rename 40 Marks blueprint section names to Section A–E

Revision ID: c6d7e8f9a0b1
Revises: b5c6d7e8f9a0
Create Date: 2026-07-29 21:15:00.000000

"""

from __future__ import annotations

import copy
import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c6d7e8f9a0b1"
down_revision: str | Sequence[str] | None = "b5c6d7e8f9a0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_LEGACY_SECTION_NAMES = ("MCQ", "VSA", "SA", "LA", "CBQ")


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
    from app.services.generation.sample_blueprints_data import FORTY_MARKS_BLUEPRINT

    legacy = copy.deepcopy(FORTY_MARKS_BLUEPRINT)
    for section, name in zip(legacy["sections"], _LEGACY_SECTION_NAMES, strict=True):
        section["section_name"] = name

    op.execute(
        sa.text(
            """
            UPDATE sample_blueprints
            SET blueprint = CAST(:blueprint AS jsonb),
                updated_at = now()
            WHERE slug = '40-marks'
            """
        ).bindparams(blueprint=json.dumps(legacy))
    )
