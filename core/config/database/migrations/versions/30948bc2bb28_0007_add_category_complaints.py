"""0007_add_category_complaints

Revision ID: 30948bc2bb28
Revises: b3301ac707c7
Create Date: 2024-07-04 12:32:10.476521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from core.apps.quiz.models import CategoryComplaint


# revision identifiers, used by Alembic.
revision: str = '30948bc2bb28'
down_revision: Union[str, None] = 'b3301ac707c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category_complaints',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_complaints_id'), 'category_complaints', ['id'], unique=True)
    op.add_column('complaints', sa.Column('category_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'complaints', 'category_complaints', ['category_id'], ['id'])
    # ### end Alembic commands ###
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()
    categories = ["Ошибка в содержании вопроса", "Ошибка в ответах", "Вопрос устарел/неактуален",
                  "Орфографическая ошибка", "Другая причина", ]

    for category in categories:
        cat = CategoryComplaint(
            name=category
        )
        session.add(cat)
        session.commit()


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'complaints', type_='foreignkey')
    op.drop_column('complaints', 'category_id')
    op.drop_index(op.f('ix_category_complaints_id'), table_name='category_complaints')
    op.drop_table('category_complaints')
    # ### end Alembic commands ###
