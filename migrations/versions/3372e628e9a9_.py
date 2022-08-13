"""empty message

Revision ID: 3372e628e9a9
Revises: 3a33261273ee
Create Date: 2022-08-13 19:43:53.624130

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3372e628e9a9'
down_revision = '3a33261273ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('show_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('shows')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shows',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('show_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='shows_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='shows_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='shows_pkey')
    )
    op.drop_table('Show')
    # ### end Alembic commands ###
