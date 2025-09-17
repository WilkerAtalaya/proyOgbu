"""Cambios para el id_area: migrar citas.area -> citas.area_id (FK)"""

from alembic import op
import sqlalchemy as sa

# Revisiones Alembic
revision = "63ce85a97962"
down_revision = "5edb9ca7eda7"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Agregar area_id como NULLABLE para poder rellenar
    with op.batch_alter_table("citas", schema=None) as batch_op:
        batch_op.add_column(sa.Column("area_id", sa.Integer(), nullable=True))

    # 2) Backfill desde texto 'area' -> id_area
    op.execute("""
        UPDATE citas c
        SET area_id = a.id_area
        FROM areas a
        WHERE c.area_id IS NULL
          AND c.area IS NOT NULL
          AND a.area = c.area;
    """)

    # 2b) Backfill alterno por motivo (por si alguna fila no tenía el nombre exacto del área)
    op.execute("""
        UPDATE citas c
        SET area_id = m.id_area
        FROM motivo_cita m
        WHERE c.area_id IS NULL
          AND LOWER(c.motivo) = LOWER(m.motivo);
    """)

    # (Opcional) Si quieres forzar que no quede ningún NULL, puedes verificar antes de seguir:
    # Si aun quedan NULLs, esta ALTER fallará y te avisará qué filas debes corregir.

    # 3) Eliminar unique viejo basado en 'area' (si existe)
    try:
        op.drop_constraint('uq_citas_area_fecha_horario', 'citas', type_='unique')
    except Exception:
        pass  # por si ya no existe

    # 4) Hacer NOT NULL, crear FK y unique nuevo
    with op.batch_alter_table("citas", schema=None) as batch_op:
        batch_op.alter_column("area_id",
                              existing_type=sa.Integer(),
                              nullable=False)
        batch_op.create_foreign_key(
            "fk_citas_area",
            "areas",
            ["area_id"],
            ["id_area"],
            ondelete=None,
        )
        batch_op.create_unique_constraint(
            "uq_citas_areaid_fecha_horario",
            ["area_id", "fecha", "horario"]
        )

    # 5) Borrar la columna antigua de texto
    with op.batch_alter_table("citas", schema=None) as batch_op:
        try:
            batch_op.drop_column("area")
        except Exception:
            pass


def downgrade():
    # Volver a tener 'area' (texto) y eliminar area_id/FK
    with op.batch_alter_table("citas", schema=None) as batch_op:
        batch_op.add_column(sa.Column("area", sa.VARCHAR(length=100), nullable=True))

    # Rellenar 'area' desde el id (para no perder datos)
    op.execute("""
        UPDATE citas c
        SET area = a.area
        FROM areas a
        WHERE c.area_id = a.id_area;
    """)

    # Restaurar unique antiguo
    with op.batch_alter_table("citas", schema=None) as batch_op:
        try:
            batch_op.drop_constraint("uq_citas_areaid_fecha_horario", type_="unique")
        except Exception:
            pass
        try:
            batch_op.drop_constraint("fk_citas_area", type_="foreignkey")
        except Exception:
            pass
        batch_op.create_unique_constraint(
            "uq_citas_area_fecha_horario",
            ["area", "fecha", "horario"]
        )
        batch_op.drop_column("area_id")
