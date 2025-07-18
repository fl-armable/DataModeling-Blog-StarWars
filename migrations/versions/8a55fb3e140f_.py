"""empty message

Revision ID: 8a55fb3e140f
Revises: 68f7f5a60498
Create Date: 2025-06-09 17:30:25.216720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a55fb3e140f'
down_revision = '68f7f5a60498'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('password', sa.String(length=50), nullable=False))
        batch_op.drop_constraint('user_username_key', type_='unique')
        batch_op.create_unique_constraint(None, ['email'])
        batch_op.drop_column('username')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('user_username_key', ['username'])
        batch_op.drop_column('password')
        batch_op.drop_column('email')

    # ### end Alembic commands ###
