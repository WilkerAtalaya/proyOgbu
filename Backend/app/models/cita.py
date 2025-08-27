from app import db
from datetime import datetime

class Cita(db.Model):
    __tablename__ = 'citas'

    id_cita = db.Column(db.Integer, primary_key=True)

    # Alumno (titular de la cita)
    id_alumno = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Datos de la cita
    motivo = db.Column(db.String(255), nullable=False, default='Salud Mental')
    descripcion = db.Column(db.Text, nullable=True)  # opcional por confidencialidad
    area = db.Column(db.String(100), nullable=False)  # 'Psicología' | 'Trabajo Social'
    fecha = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), default='Solicitado')  # Solicitado|Aprobado|Reprogramado|Atendido|Ausente
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Quién registró la cita (admin/alumno/staff)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # --- Reprogramación (handshake: solicitud + confirmación) ---
    reprog_fecha = db.Column(db.Date, nullable=True)
    reprog_horario = db.Column(db.String(50), nullable=True)
    reprog_solicitada_por = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    reprog_estado = db.Column(db.String(20), nullable=True)          # Pendiente | Aceptada | Rechazada
    reprog_pendiente_para = db.Column(db.String(20), nullable=True)  # 'Alumno' | 'Staff'

    # Argumentos/evidencia de la solicitud (del alumno)
    reprog_motivo = db.Column(db.Text, nullable=True)
    reprog_evid_bucket = db.Column(db.String(50), nullable=True)
    reprog_evid_name = db.Column(db.String(255), nullable=True)

    # Relaciones
    alumno = db.relationship('Usuario', foreign_keys=[id_alumno])
    creador = db.relationship('Usuario', foreign_keys=[id_usuario])
    solicitante_reprog = db.relationship('Usuario', foreign_keys=[reprog_solicitada_por])

    # Índices/constraints de tabla
    __table_args__ = (
        db.UniqueConstraint('area', 'fecha', 'horario', name='uq_citas_area_fecha_horario'),
    )