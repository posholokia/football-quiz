"""0014_cascade_delete_question

Revision ID: 3b783468c1c0
Revises: 6bd5d91a4387
Create Date: 2024-08-06 20:45:13.047504

"""
from typing import (
    Sequence,
    Union,
)

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b783468c1c0'
down_revision: Union[str, None] = '6bd5d91a4387'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_answers_question_id'), 'answers', ['question_id'], unique=False)
    op.drop_constraint('answers_question_id_fkey', 'answers', type_='foreignkey')
    op.create_foreign_key(None, 'answers', 'questions', ['question_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_complaints_question_id'), 'complaints', ['question_id'], unique=False)
    op.drop_constraint('complaints_question_id_fkey', 'complaints', type_='foreignkey')
    op.create_foreign_key(None, 'complaints', 'questions', ['question_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'complaints', type_='foreignkey')
    op.create_foreign_key('complaints_question_id_fkey', 'complaints', 'questions', ['question_id'], ['id'])
    op.drop_index(op.f('ix_complaints_question_id'), table_name='complaints')
    op.drop_constraint(None, 'answers', type_='foreignkey')
    op.create_foreign_key('answers_question_id_fkey', 'answers', 'questions', ['question_id'], ['id'])
    op.drop_index(op.f('ix_answers_question_id'), table_name='answers')
    # ### end Alembic commands ###
