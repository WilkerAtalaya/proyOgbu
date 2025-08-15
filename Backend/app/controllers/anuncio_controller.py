from app.models.anuncio import Publicacion
from app import db

def crear_anuncio(data):
    # Contar cuántos anuncios hay
    total_anuncios = Publicacion.query.count()

    # Si ya hay 15 o más, eliminar el más antiguoo
    if total_anuncios >= 15:
        anuncio_mas_antiguo = Publicacion.query.order_by(Publicacion.fecha_publicacion.asc()).first()
        if anuncio_mas_antiguo:
            db.session.delete(anuncio_mas_antiguo)
            db.session.commit()

    nuevo = Publicacion(
        titulo=data.get('titulo'),
        descripcion=data.get('descripcion'),
        imagen=data.get('imagen'),
        id_usuario=data.get('id_usuario')
    )

    db.session.add(nuevo)
    db.session.commit()
    return nuevo


def obtener_anuncios():
    return Publicacion.query.order_by(Publicacion.fecha_publicacion.desc()).limit(15).all()

def obtener_anuncio_por_id(id_publicacion: int):
    return Publicacion.query.get(id_publicacion)


def actualizar_anuncio(
    id_publicacion: int,
    titulo: str | None = None,
    descripcion: str | None = None,
    imagen: str | None = None
):
    anuncio = Publicacion.query.get(id_publicacion)
    if not anuncio:
        return None

    if titulo is not None:
        anuncio.titulo = titulo
    if descripcion is not None:
        anuncio.descripcion = descripcion
    if imagen is not None:
        anuncio.imagen = imagen if imagen != '' else None

    db.session.commit()
    return anuncio


def eliminar_anuncio(id_publicacion: int):
    anuncio = Publicacion.query.get(id_publicacion)
    if not anuncio:
        return None
    db.session.delete(anuncio)
    db.session.commit()
    return True