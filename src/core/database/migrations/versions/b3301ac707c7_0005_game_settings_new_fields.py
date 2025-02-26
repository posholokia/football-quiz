"""0006_game_settings_new_fields

Revision ID: b3301ac707c7
Revises: 2b6ae75e005d
Create Date: 2024-06-30 20:24:30.278855

"""
from typing import (
    Sequence,
    Union,
)

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3301ac707c7'
down_revision: Union[str, None] = '2b6ae75e005d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_settings', sa.Column('recovery_period', sa.Integer(), nullable=False, server_default="600"))
    op.add_column('game_settings', sa.Column('recovery_value', sa.Integer(), nullable=False, server_default="10"))
    # ### end Alembic commands ###
    op.alter_column('game_settings', 'recovery_period', server_default=None)
    op.alter_column('game_settings', 'recovery_value', server_default=None)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game_settings', 'recovery_value')
    op.drop_column('game_settings', 'recovery_period')
    # ### end Alembic commands ###
