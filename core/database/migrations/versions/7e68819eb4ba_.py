"""

Revision ID: 7e68819eb4ba
Revises: 1ffc223c1a3b
Create Date: 2024-05-28 22:55:33.217890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e68819eb4ba'
down_revision: Union[str, None] = '1ffc223c1a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'statictics', ['place'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'statictics', type_='unique')
    # ### end Alembic commands ###
