"""Cambiar fecha_salida y fecha_regreso de Date a DateTime con timezone

Revision ID: ef64f04e9c52
Revises: 9ebb7c01a763
Create Date: 2025-08-27 19:41:17.628457

"""
from alembic import op
import sqlalchemy as sa


revision = 'ef64f04e9c52'
down_revision = '9ebb7c01a763'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('salidas_vivienda', 'fecha_salida',
                   existing_type=sa.DATE(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=False)
    
    op.alter_column('salidas_vivienda', 'fecha_regreso',
                   existing_type=sa.DATE(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=False)


def downgrade():
    op.alter_column('salidas_vivienda', 'fecha_regreso',
                   existing_type=sa.DateTime(timezone=True),
                   type_=sa.DATE(),
                   existing_nullable=False)
    
    op.alter_column('salidas_vivienda', 'fecha_salida',
                   existing_type=sa.DateTime(timezone=True),
                   type_=sa.DATE(),
                   existing_nullable=False)
