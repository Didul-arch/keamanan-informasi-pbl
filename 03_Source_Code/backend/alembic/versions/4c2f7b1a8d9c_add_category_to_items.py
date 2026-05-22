"""add category to items

Revision ID: 4c2f7b1a8d9c
Revises: 6e638497260a
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c2f7b1a8d9c'
down_revision: Union[str, None] = '6e638497260a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('items', sa.Column('category', sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column('items', 'category')
