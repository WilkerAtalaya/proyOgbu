from app import db
from datetime import datetime

class Queja(db.Model):
    __tablename__ = 'quejas'

    id_queja = db.Column(db.Integer, primary_key=True)
    codigo_reporte = db.Column(db.String(20), unique=True, nullable=False)
    asunto = db.Column(db.String(255), nullable=False)
    motivo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    prueba = db.Column(db.String(255))  # Ruta o nombre de la imagen
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='Recibido')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
