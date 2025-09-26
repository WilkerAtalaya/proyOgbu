from datetime import datetime
from app.models.usuarios import Usuario
from app.models.rol import Rol 
from sqlalchemy import or_, func
from app import db
from app.models.reconocimiento import Reconocimiento

def crear_reconocimiento(data):
    id_alumno = data.get("id_alumno")

    alumno = Usuario.query.get(id_alumno)
    if not alumno or alumno.rol != "alumno":
        raise ValueError("Alumno no válido")

    nuevo = Reconocimiento(
        id_alumno=id_alumno,
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
    termino = (termino or "").strip()
    q = (Usuario.query
         .join(Usuario.rol_rel)          
         .filter(Rol.slug == "alumno"))  

    if termino:
        q = q.filter(Usuario.nombre.ilike(f"%{termino}%"))  
    return q.order_by(Usuario.nombre.asc()).all()

def eliminar_reconocimiento(id_reconocimiento):
    reconocimiento = Reconocimiento.query.get(id_reconocimiento)
    if not reconocimiento:
        return False  
    db.session.delete(reconocimiento)
    db.session.commit()
    return True
