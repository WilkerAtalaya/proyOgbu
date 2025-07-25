from app import db
from datetime import datetime
from pytz import timezone
from app.models.usuarios import Usuario

class RegistroAsistencia(db.Model):
    __tablename__ = 'asistencias'

    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    fecha = db.Column(db.Date, default=lambda: datetime.now(timezone('America/Lima')).date())
    hora_marcado = db.Column(db.DateTime, default=lambda: datetime.now(timezone('America/Lima')))

    alumno = db.relationship('Usuario', backref='asistencias', lazy=True)

    def to_dict(self):
        return {
            'id': self.id_asistencia,
            'id_usuario': self.id_usuario,
            'nombre_alumno': self.alumno.nombre if self.alumno else None,
            'fecha': self.fecha.isoformat(),
            'hora_marcado': self.hora_marcado.isoformat()
        }

