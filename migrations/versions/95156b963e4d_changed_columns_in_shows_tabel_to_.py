"""changed columns in shows tabel to DateTime

Revision ID: 95156b963e4d
Revises: 0673f05686e4
Create Date: 2024-10-21 21:55:53.799154

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '95156b963e4d'
down_revision = '0673f05686e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Shows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('showtime', sa.DateTime(), nullable=True))
        batch_op.drop_column('show_date')
        batch_op.drop_column('show_time')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Shows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('show_time', postgresql.TIME(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('show_date', sa.DATE(), autoincrement=False, nullable=True))
        batch_op.drop_column('showtime')

    # ### end Alembic commands ###