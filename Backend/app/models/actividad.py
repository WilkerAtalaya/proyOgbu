from app import db
from datetime import datetime

class Actividad(db.Model):
    __tablename__ = 'actividades'

    id_actividad = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_actividad = db.Column(db.DateTime, nullable=False)
    archivo = db.Column(db.String(255))  
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='Pendiente')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)