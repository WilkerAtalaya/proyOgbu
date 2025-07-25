from datetime import datetime
from app import db

class SalidaVivienda(db.Model):
    __tablename__ = 'salidas_vivienda'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    fecha_regreso = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default='En revisión')  # En revisión, Aprobado, Denegado

    usuario = db.relationship('Usuario', backref='salidas')

    def to_dict(self):
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'fecha_salida': self.fecha_salida.strftime('%Y-%m-%d'),
            'fecha_regreso': self.fecha_regreso.strftime('%Y-%m-%d'),
            'motivo': self.motivo,
            'estado': self.estado
        }


class ReservaAreaComun(db.Model):
    __tablename__ = 'reservas_area_comun'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    lugar = db.Column(db.String(50), nullable=False)  # Hall, patio, lavandería, sala de computo
    fecha = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), default='En revisión')  # En revisión, Aprobado, Denegado

    usuario = db.relationship('Usuario', backref='reservas')

    def to_dict(self):
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'lugar': self.lugar,
            'fecha': self.fecha.strftime('%Y-%m-%d'),
            'horario': self.horario,
            'estado': self.estado
        }
