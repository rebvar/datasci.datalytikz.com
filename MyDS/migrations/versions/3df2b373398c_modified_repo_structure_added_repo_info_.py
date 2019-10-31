"""Modified Repo Structure, added repo info and dates

Revision ID: 3df2b373398c
Revises: cbce88b02f0a
Create Date: 2018-08-07 01:23:51.874737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3df2b373398c'
down_revision = 'cbce88b02f0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Repos', sa.Column('cloneFinishDate', sa.String(), nullable=True))
    op.add_column('Repos', sa.Column('cloneStartDate', sa.String(), nullable=True))
    op.add_column('Repos', sa.Column('isPrivate', sa.Integer(), nullable=True))
    op.add_column('Repos', sa.Column('repoInfo', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Repos', 'repoInfo')
    op.drop_column('Repos', 'isPrivate')
    op.drop_column('Repos', 'cloneStartDate')
    op.drop_column('Repos', 'cloneFinishDate')
    # ### end Alembic commands ###
