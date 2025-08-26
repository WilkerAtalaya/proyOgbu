"""Agregar campo titulo a publicaciones

Revision ID: e3d31ca3598a
Revises: c0b2e6e4b31a
Create Date: 2025-08-15 11:16:44.312269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3d31ca3598a'
down_revision = 'c0b2e6e4b31a'
branch_labels = None
depends_on = None


def upgrade():
    # 1) crear la columna con DEFAULT para no romper por NOT NULL
    op.add_column(
        'publicaciones',
        sa.Column('titulo', sa.String(length=150), nullable=False, server_default='Sin título')
    )
    # 2) quitar el DEFAULT para que en adelante sea obligatorio sin valor por defecto
    op.alter_column('publicaciones', 'titulo', server_default=None)

def downgrade():
    op.drop_column('publicaciones', 'titulo')


