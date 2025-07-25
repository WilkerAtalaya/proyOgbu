from app import db
from datetime import datetime

class Cita(db.Model):
    __tablename__ = 'citas'

    id_cita = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(100), nullable=False)  # Bienestar o Psicologia
    fecha = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), default='Solicitado')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)  # quien registró la cita

    alumno = db.relationship('Usuario', foreign_keys=[id_alumno])
    creador = db.relationship('Usuario', foreign_keys=[id_usuario])