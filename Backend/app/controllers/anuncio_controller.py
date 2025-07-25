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
        descripcion=data.get('descripcion'),
        imagen=data.get('imagen'),
        id_usuario=data.get('id_usuario')
    )

    db.session.add(nuevo)
    db.session.commit()
    return nuevo


def obtener_anuncios():
    return Publicacion.query.order_by(Publicacion.fecha_publicacion.desc()).limit(15).all()
