"""Added RevisionData Table

Revision ID: 9f422509e726
Revises: 0907edc6ba17
Create Date: 2018-08-22 11:29:32.221397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f422509e726'
down_revision = '0907edc6ba17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('RevisionData',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('repoFileId', sa.Integer(), nullable=False),
    sa.Column('repoId', sa.Integer(), nullable=False),
    sa.Column('rev', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('revIndex', sa.Integer(), nullable=True),
    sa.Column('gDump', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['repoFileId'], ['RepoFile.id'], ),
    sa.ForeignKeyConstraint(['repoId'], ['Repo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('RevisionData')
    # ### end Alembic commands ###
