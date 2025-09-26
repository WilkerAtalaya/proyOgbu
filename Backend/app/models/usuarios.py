from app import db
from sqlalchemy.sql import func
from app.models.rol import Rol

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)

    # Datos básicos
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)

    fecha_cumpleaños = db.Column('fecha_cumpleaños', db.Date, nullable=True)

    estado = db.Column(db.String(10), nullable=True)         
    residencia = db.Column(db.String(20), nullable=True)     
    pabellon = db.Column(db.String(20), nullable=True)       
    habitacion = db.Column(db.String(20), nullable=True)      
    fecha_registro = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # === Nuevo esquema de roles ===
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    rol_rel = db.relationship('Rol', back_populates='usuarios')

    # --------- Helpers / compatibilidad ----------
    @property
    def rol_slug(self) -> str | None:
        """Slug del rol (admin, alumno, psicologia, social, ...)."""
        return self.rol_rel.slug if self.rol_rel else None

    @property
    def rol_area_id(self) -> int | None:
        """Área asociada al rol (si aplica: psicología/social)."""
        return self.rol_rel.area_id if self.rol_rel else None

    @property
    def rol(self) -> str | None:
        return self.rol_slug

    # --------- Serialización básica ----------
    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "correo": self.correo,
            "estado": self.estado,
            "residencia": self.residencia,
            "pabellon": self.pabellon,
            "habitacion": self.habitacion,
            "fecha_cumpleanos": self.fecha_cumpleanos.isoformat() if self.fecha_cumpleanos else None,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "rol_id": self.rol_id,
            "rol": self.rol_slug,
            "rol_nombre": self.rol_rel.nombre if self.rol_rel else None,
            "area_id": self.rol_area_id,
            "area": self.rol_rel.area.area if (self.rol_rel and self.rol_rel.area) else None,
        }

    def __repr__(self):
        return f"<Usuario id={self.id_usuario} nombre={self.nombre} rol={self.rol_slug}>"
