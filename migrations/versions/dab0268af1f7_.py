"""empty message

Revision ID: dab0268af1f7
Revises: 3372e628e9a9
Create Date: 2022-08-13 20:11:20.937827

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dab0268af1f7'
down_revision = '3372e628e9a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.drop_column('Show', 'show_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('show_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###
