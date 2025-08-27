from app import db
from datetime import datetime, timezone

class InscripcionActividad(db.Model):
    __tablename__ = 'inscripciones_actividad'

    id_inscripcion = db.Column(db.Integer, primary_key=True)
    id_actividad   = db.Column(db.Integer, db.ForeignKey('actividades.id_actividad', ondelete='CASCADE'), nullable=False)
    id_usuario     = db.Column(db.Integer,db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    actividad = db.relationship('Actividad', backref='inscripciones', lazy=True)
    alumno    = db.relationship('Usuario',   backref='inscripciones', lazy=True)
