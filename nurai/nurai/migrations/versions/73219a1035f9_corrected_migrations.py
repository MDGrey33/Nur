"""Corrected migrations

Revision ID: 73219a1035f9
Revises: d69322653621
Create Date: 2024-04-10 23:53:16.868082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73219a1035f9'
down_revision: Union[str, None] = 'd69322653621'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('interactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('thread_ts', sa.String(length=255), nullable=True),
    sa.Column('question_text', sa.Text(), nullable=True),
    sa.Column('assistant_thread_id', sa.String(length=255), nullable=True),
    sa.Column('answer_text', sa.Text(), nullable=True),
    sa.Column('channel_id', sa.String(length=255), nullable=True),
    sa.Column('slack_user_id', sa.String(length=255), nullable=True),
    sa.Column('question_timestamp', sa.DateTime(), nullable=True),
    sa.Column('answer_timestamp', sa.DateTime(), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interactions_assistant_thread_id'), 'interactions', ['assistant_thread_id'], unique=False)
    op.create_index(op.f('ix_interactions_thread_ts'), 'interactions', ['thread_ts'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_interactions_thread_ts'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_assistant_thread_id'), table_name='interactions')
    op.drop_table('interactions')
    # ### end Alembic commands ###
