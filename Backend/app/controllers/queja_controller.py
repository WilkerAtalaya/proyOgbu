from app import db
from app.models.queja import Queja
from datetime import datetime
import random

def generar_codigo_reporte():
    return f"UNMSM-{random.randint(10000, 99999)}"

def crear_queja(data):
    nueva = Queja(
        codigo_reporte=generar_codigo_reporte(),
        asunto=data.get("asunto"),
        motivo=data.get("motivo"),
        descripcion=data.get("descripcion"),
        prueba=data.get("prueba"),
        id_usuario=data.get("id_usuario")
    )
    db.session.add(nueva)
    db.session.commit()
    return nueva

def obtener_quejas_por_usuario(id_usuario):
    return Queja.query.filter_by(id_usuario=id_usuario).order_by(Queja.fecha.desc()).all()

def obtener_todas_quejas():
    return Queja.query.order_by(Queja.fecha.desc()).all()

def actualizar_estado_queja(id_queja, nuevo_estado):
    queja = Queja.query.get(id_queja)
    if queja:
        queja.estado = nuevo_estado
        db.session.commit()
    return queja
