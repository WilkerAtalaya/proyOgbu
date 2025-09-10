from app import db
from sqlalchemy import CheckConstraint, func

ROLES_PERMITIDOS = ("alumno", "admin", "psicologia", "social")
ESTADOS_PERMITIDOS = ("activo", "inactivo")
RESIDENCIAS_PERMITIDAS = ("Ciudad", "Tello")


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False, index=True)
    contraseña = db.Column(db.String(255), nullable=False)

    # IMPORTANTE: el rol válido para administrador es 'admin'
    rol = db.Column(db.String(20), nullable=False)

    fecha_cumpleaños = db.Column(db.Date)

    # === NUEVAS COLUMNAS ===
    estado = db.Column(db.String(10), nullable=False, server_default="activo", index=True)
    residencia = db.Column(db.String(10))  # 'Ciudad' o 'Tello'
    pabellon = db.Column(db.String(20))
    habitacion = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    __table_args__ = (
        CheckConstraint(rol.in_(ROLES_PERMITIDOS), name="ck_usuarios_rol"),
        CheckConstraint(estado.in_(ESTADOS_PERMITIDOS), name="ck_usuarios_estado"),
        CheckConstraint(
            db.or_(residencia.is_(None), residencia.in_(RESIDENCIAS_PERMITIDAS)),
            name="ck_usuarios_residencia"
        ),
    )