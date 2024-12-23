"""Add compare_items column as JSON in User table

Revision ID: 38071906651d
Revises: dad7c948d647
Create Date: 2024-12-18 13:32:16.320497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38071906651d'
down_revision: Union[str, None] = 'dad7c948d647'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('compare_items', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'compare_items')
    # ### end Alembic commands ###
