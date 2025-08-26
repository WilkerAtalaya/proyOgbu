from app import db
from app.models.queja import Queja
from app.models.usuarios import Usuario
from sqlalchemy import func
from datetime import datetime, timedelta
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

def obtener_todas_quejas(filtros: dict | None = None):
    q = db.session.query(Queja)

    if filtros:
        if filtros.get('estado'):
            q = q.filter(Queja.estado == filtros['estado'])

        if filtros.get('motivo'):
            q = q.filter(Queja.motivo.ilike(f"%{filtros['motivo']}%"))

        # ✅ FILTRO POR NOMBRE usando Usuario.nombre
        if filtros.get('nombre'):
            q = q.join(Usuario, Usuario.id_usuario == Queja.id_usuario)
            q = q.filter(Usuario.nombre.ilike(f"%{filtros['nombre'].strip()}%"))

        if filtros.get('fecha_desde'):
            q = q.filter(Queja.fecha >= filtros['fecha_desde'])
        if filtros.get('fecha_hasta'):
            from datetime import timedelta
            q = q.filter(Queja.fecha < (filtros['fecha_hasta'] + timedelta(days=1)))

    return q.order_by(Queja.fecha.desc()).all()

def actualizar_estado_queja(id_queja, nuevo_estado):
    queja = Queja.query.get(id_queja)
    if queja:
        queja.estado = nuevo_estado
        db.session.commit()
    return queja

def actualizar_queja_por_alumno(
    id_queja: int,
    id_usuario: int,
    asunto: str | None = None,
    motivo: str | None = None,
    descripcion: str | None = None,
    prueba: str | None = None 
):
    queja = Queja.query.get(id_queja)
    if not queja:
        return None, "NOT_FOUND"

    if int(queja.id_usuario) != int(id_usuario):
        return None, "FORBIDDEN"

    
    if queja.estado != "Recibido":
        return None, "LOCKED" 

    if asunto is not None:
        queja.asunto = asunto
    if motivo is not None:
        queja.motivo = motivo
    if descripcion is not None:
        queja.descripcion = descripcion
    if prueba is not None:
        queja.prueba = (None if prueba == '' else prueba)

    db.session.commit()
    return queja, None

