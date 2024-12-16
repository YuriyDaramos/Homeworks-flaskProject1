"""Remove test_field column from search_history table

Revision ID: dad7c948d647
Revises: 91e863408a95
Create Date: 2024-11-20 22:07:43.437314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dad7c948d647'
down_revision: Union[str, None] = '91e863408a95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('search_history', 'test_field')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('search_history', sa.Column('test_field', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###