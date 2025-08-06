from datetime import datetime
from app.models.usuarios import Usuario
from sqlalchemy import or_, func
from app import db
from app.models.reconocimiento import Reconocimiento

def crear_reconocimiento(data):
    nuevo = Reconocimiento(
        id_alumno=data.get("id_alumno"),
        descripcion=data.get("descripcion"),
        fecha_reconocimiento=datetime.now(),
        id_usuario=data.get("id_usuario") 
    )
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_reconocimientos():
    return Reconocimiento.query.order_by(Reconocimiento.fecha_reconocimiento.desc()).all()

def buscar_alumnos_por_nombre(termino):
    termino_busqueda = f"%{termino.lower()}%"
    return Usuario.query.filter(
        func.lower(Usuario.rol) == "alumno",
        or_(
            func.lower(Usuario.nombre).like(termino_busqueda)
        )
    ).all()