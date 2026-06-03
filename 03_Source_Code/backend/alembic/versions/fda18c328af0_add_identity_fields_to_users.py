"""add identity fields to users

Revision ID: fda18c328af0
Revises: 4c2f7b1a8d9c
Create Date: 2026-05-24 07:25:32.962539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fda18c328af0'
down_revision: Union[str, None] = '4c2f7b1a8d9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('identity_number', sa.String(), nullable=True))
    op.add_column('users', sa.Column('identity_document', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'identity_document')
    op.drop_column('users', 'identity_number')