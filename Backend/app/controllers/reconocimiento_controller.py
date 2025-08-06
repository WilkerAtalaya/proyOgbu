from datetime import datetime
from app.models.usuarios import Usuario
from sqlalchemy import or_, func
from app import db
from app.models.reconocimiento import Reconocimiento

def crear_reconocimiento(data):
    nombre_alumno = data.get("nombre_alumno")
    alumno = Usuario.query.filter(
        func.lower(Usuario.nombre) == func.lower(nombre_alumno),
        Usuario.rol == "alumno"
    ).first()

    if not alumno:
        raise ValueError("Alumno no encontrado")

    nuevo = Reconocimiento(
        id_alumno=alumno.id_usuario,
        descripcion=data.get("descripcion"),
        fecha_reconocimiento=datetime.now(),
        id_usuario=data.get("id_usuario")
    )
    db.session.add(nuevo)
    db.session.commit()
    return nuevo, alumno.nombre


def obtener_reconocimientos():
    return db.session.query(Reconocimiento, Usuario).join(
        Usuario, Usuario.id_usuario == Reconocimiento.id_alumno
    ).order_by(Reconocimiento.fecha_reconocimiento.desc()).all()


def buscar_alumnos_por_nombre(termino):
    termino_busqueda = f"%{termino.lower()}%"
    return Usuario.query.filter(
        func.lower(Usuario.rol) == "alumno",
        or_(
            func.lower(Usuario.nombre).like(termino_busqueda)
        )
    ).all()

def eliminar_reconocimiento(id_reconocimiento):
    reconocimiento = Reconocimiento.query.get(id_reconocimiento)
    if not reconocimiento:
        return False  
    db.session.delete(reconocimiento)
    db.session.commit()
    return True
