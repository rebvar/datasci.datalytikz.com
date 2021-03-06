"""Added graphtype column to RevisionData

Revision ID: 496ababc041b
Revises: 9f422509e726
Create Date: 2018-08-23 01:24:14.781378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '496ababc041b'
down_revision = '9f422509e726'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('RevisionData', sa.Column('graphType', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('RevisionData', 'graphType')
    # ### end Alembic commands ###
