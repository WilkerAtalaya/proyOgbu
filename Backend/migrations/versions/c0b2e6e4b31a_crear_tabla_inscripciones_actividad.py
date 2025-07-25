"""crear tabla inscripciones_actividad

Revision ID: c0b2e6e4b31a
Revises: 646c2322fa63
Create Date: 2025-07-14 16:22:57.799518

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0b2e6e4b31a'
down_revision = '646c2322fa63'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inscripciones_actividad',
    sa.Column('id_inscripcion', sa.Integer(), nullable=False),
    sa.Column('id_actividad', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('fecha_registro', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_actividad'], ['actividades.id_actividad'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_inscripcion')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inscripciones_actividad')
    # ### end Alembic commands ###
