from app import db

class Reconocimiento(db.Model):
    __tablename__ = 'reconocimientos'

    id_reconocimiento = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)  # Relación a alumno
    descripcion = db.Column(db.Text, nullable=False)
    fecha_reconocimiento = db.Column(db.DateTime, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)  # Relación a admin
