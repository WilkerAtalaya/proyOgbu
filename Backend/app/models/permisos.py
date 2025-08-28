# app/models/permisos.py
from datetime import datetime, timezone
from app import db

class SalidaVivienda(db.Model):
    __tablename__ = 'salidas_vivienda'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_salida = db.Column(db.DateTime(timezone=True), nullable=False)
    fecha_regreso = db.Column(db.DateTime(timezone=True), nullable=False)
    motivo = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default='En revisión')  # En revisión, Aprobado, Denegado
    archivo_justificacion = db.Column(db.String(255))         # guardamos el nombre/relativo del archivo
    Fecha_solicitada = db.Column(db.DateTime(timezone=True), nullable=False,
                          default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship('Usuario', backref='salidas')


class ReservaAreaComun(db.Model):
    __tablename__ = 'reservas_area_comun'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    lugar = db.Column(db.String(50), nullable=False)  # Hall, patio, lavandería, sala de computo
    fecha = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), default='En revisión')  # En revisión, Aprobado, Denegado
    motivo = db.Column(db.Text, nullable=True)
    Fecha_solicitada = db.Column(db.DateTime(timezone=True), nullable=False,
                          default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship('Usuario', backref='reservas')
