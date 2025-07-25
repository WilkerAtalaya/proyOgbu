"""Migración actualizar tabla asistencia

Revision ID: 01d781f2c441
Revises: 9f3191a0934c
Create Date: 2025-06-12 23:46:26.524406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01d781f2c441'
down_revision = '9f3191a0934c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asistencias', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha', sa.Date(), nullable=True))
        batch_op.create_foreign_key(None, 'usuarios', ['codigo_alumno'], ['codigo_alumno'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asistencias', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('fecha')

    # ### end Alembic commands ###
