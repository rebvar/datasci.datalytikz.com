"""Added Registration Field to User

Revision ID: 014faf0389b8
Revises: 5a8e9ac5ac7d
Create Date: 2018-08-13 15:37:55.587522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014faf0389b8'
down_revision = '5a8e9ac5ac7d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('registrationDate', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'registrationDate')
    # ### end Alembic commands ###
