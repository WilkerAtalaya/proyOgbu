from app import db
from datetime import datetime, timezone

class Publicacion(db.Model):
    __tablename__ = 'publicaciones'

    id_publicacion = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    imagen = db.Column(db.String(255))
    fecha_publicacion = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
