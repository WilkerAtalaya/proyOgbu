from app.models.anuncio import Publicacion
from app import db

def crear_anuncio(data):
    total_anuncios = Publicacion.query.count()
    if total_anuncios >= 15:
        ant = Publicacion.query.order_by(Publicacion.fecha_publicacion.asc()).first()
        if ant:
            db.session.delete(ant)
            db.session.commit()

    nuevo = Publicacion(
        titulo=data.get('titulo'),
        descripcion=data.get('descripcion'),
        imagen=data.get('imagen'),  # guardamos SOLO el nombre almacenado
        id_usuario=data.get('id_usuario')
    )
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def obtener_anuncios():
    return Publicacion.query.order_by(Publicacion.fecha_publicacion.desc()).limit(15).all()

def obtener_anuncio_por_id(id_publicacion: int):
    return Publicacion.query.get(id_publicacion)

def actualizar_anuncio(id_publicacion: int, titulo=None, descripcion=None, imagen=None):
    a = Publicacion.query.get(id_publicacion)
    if not a:
        return None
    if titulo is not None:
        a.titulo = titulo
    if descripcion is not None:
        a.descripcion = descripcion
    if imagen is not None:             # '' => borrar, str => reemplazar, None => no tocar
        a.imagen = (None if imagen == '' else imagen)
    db.session.commit()
    return a

def eliminar_anuncio(id_publicacion: int):
    a = Publicacion.query.get(id_publicacion)
    if not a:
        return None
    db.session.delete(a)
    db.session.commit()
    return True
