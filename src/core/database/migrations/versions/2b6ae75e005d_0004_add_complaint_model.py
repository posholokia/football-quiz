"""0005_add_complaint_model

Revision ID: 2b6ae75e005d
Revises: e6a82a62ea8b
Create Date: 2024-06-25 12:31:29.475468

"""
from typing import (
    Sequence,
    Union,
)

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b6ae75e005d'
down_revision: Union[str, None] = 'e6a82a62ea8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('complaints',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('solved', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaints_id'), 'complaints', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_complaints_id'), table_name='complaints')
    op.drop_table('complaints')
    # ### end Alembic commands ###
