from app import db
from app.models.usuarios import Usuario
from datetime import date
from sqlalchemy import extract

def obtener_cumpleaños_hoy():
    hoy = date.today()
    usuarios = Usuario.query.filter(
        extract('day', Usuario.fecha_cumpleaños) == hoy.day,
        extract('month', Usuario.fecha_cumpleaños) == hoy.month,
        Usuario.rol == 'alumno'
    ).all()
    return usuarios

