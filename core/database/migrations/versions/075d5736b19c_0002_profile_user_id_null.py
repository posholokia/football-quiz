"""0002_profile_user_id_null

Revision ID: 075d5736b19c
Revises: cfbf138d1743
Create Date: 2024-05-21 23:50:51.605550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '075d5736b19c'
down_revision: Union[str, None] = 'cfbf138d1743'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
