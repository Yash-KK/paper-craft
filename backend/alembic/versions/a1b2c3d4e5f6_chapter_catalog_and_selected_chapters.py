"""chapter_catalog_and_selected_chapters

Revision ID: a1b2c3d4e5f6
Revises: 65697479b564
Create Date: 2026-07-16 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '65697479b564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'chapter_catalog',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('book_code', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=False),
        sa.Column('grade', sa.String(length=50), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('chapter_name', sa.String(length=255), nullable=False),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('book_code', 'chapter_number', name='uq_chapter_catalog_book_chapter'),
    )
    op.create_index(
        'ix_chapter_catalog_grade_subject',
        'chapter_catalog',
        ['grade', 'subject'],
        unique=False,
    )
    op.add_column(
        'notebooks',
        sa.Column(
            'selected_chapters',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.drop_index(op.f('ix_notebook_chapters_notebook_id'), table_name='notebook_chapters')
    op.drop_table('notebook_chapters')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        'notebook_chapters',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('notebook_id', sa.UUID(), nullable=False),
        sa.Column('book_code', sa.String(length=50), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('chapter_name', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=True),
        sa.Column('grade', sa.String(length=50), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['notebook_id'], ['notebooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_notebook_chapters_notebook_id'),
        'notebook_chapters',
        ['notebook_id'],
        unique=False,
    )
    op.drop_column('notebooks', 'selected_chapters')
    op.drop_index('ix_chapter_catalog_grade_subject', table_name='chapter_catalog')
    op.drop_table('chapter_catalog')
