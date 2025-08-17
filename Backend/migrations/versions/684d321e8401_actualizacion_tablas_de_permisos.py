"""Actualizacion tablas de permisos

Revision ID: 684d321e8401
Revises: e4e60344b53a
Create Date: 2025-08-16 18:13:34.404205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '684d321e8401'
down_revision = 'e4e60344b53a'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    # --- reservas_area_comun ---
    with op.batch_alter_table('reservas_area_comun') as batch_op:
        # 1) crear con default NOW() para no romper filas existentes
        batch_op.add_column(sa.Column('Fecha_solicitada', sa.DateTime(), nullable=False,
                                      server_default=sa.text('NOW()')))
        # 2) motivo (si aún no existe)
        batch_op.add_column(sa.Column('motivo', sa.String(length=255), nullable=True))

    # Si no quiere dejar el server_default, quítelo luego del backfill:
    op.alter_column('reservas_area_comun', 'Fecha_solicitada',
                    server_default=None, existing_type=sa.DateTime(), existing_nullable=False)

    # --- salidas_vivienda ---
    with op.batch_alter_table('salidas_vivienda') as batch_op:
        # 1) archivo_justificacion: debe ser nullable (hay registros viejos sin archivo)
        batch_op.add_column(sa.Column('archivo_justificacion', sa.String(length=255), nullable=True))
        # 2) Fecha_solicitada con default temporal para backfill
        batch_op.add_column(sa.Column('Fecha_solicitada', sa.DateTime(), nullable=False,
                                      server_default=sa.text('NOW()')))

    op.alter_column('salidas_vivienda', 'Fecha_solicitada',
                    server_default=None, existing_type=sa.DateTime(), existing_nullable=False)

def downgrade():
    with op.batch_alter_table('salidas_vivienda') as batch_op:
        batch_op.drop_column('Fecha_solicitada')
        batch_op.drop_column('archivo_justificacion')

    with op.batch_alter_table('reservas_area_comun') as batch_op:
        batch_op.drop_column('motivo')
        batch_op.drop_column('Fecha_solicitada')

