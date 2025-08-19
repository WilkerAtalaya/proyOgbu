from flask import Blueprint, request, jsonify
from app.controllers.anuncio_controller import (
    crear_anuncio, obtener_anuncios, obtener_anuncio_por_id,
    actualizar_anuncio, eliminar_anuncio
)
from app.files.service import save_upload, delete_file, file_url
from datetime import datetime

anuncio_bp = Blueprint('anuncio', __name__)
BUCKET = 'anuncios'

def to_archivo_obj(stored_name: str | None):
    if not stored_name:
        return None
    return {
        "bucket": BUCKET,
        "stored_name": stored_name,
        "original_name": stored_name.split('_', 1)[-1] if '_' in stored_name else stored_name,
        "mime": None,
        "size": None,
        "url": file_url(BUCKET, stored_name, external=False)
    }

@anuncio_bp.route('/anuncios', methods=['GET'])
def listar_anuncios():
    anuncios = obtener_anuncios()
    return jsonify([{
        'id': a.id_publicacion,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'imagen': file_url(BUCKET, a.imagen, external=False) if a.imagen else None,
        'archivo': to_archivo_obj(a.imagen),
        'fecha_publicacion': a.fecha_publicacion.isoformat()
    } for a in anuncios])


@anuncio_bp.route('/anuncios', methods=['POST'])
def publicar_anuncio():
    titulo = (request.form.get('titulo') or '').strip()
    if not titulo:
        return jsonify({'mensaje': 'El campo "titulo" es obligatorio'}), 400
    descripcion = (request.form.get('descripcion') or '').strip()
    if not descripcion:
        return jsonify({'mensaje': 'El campo "descripcion" es obligatorio'}), 400

    id_usuario = request.form.get('id_usuario')
    imagen_name = None

    if 'imagen' in request.files and request.files['imagen'].filename:
        meta, err = save_upload(request.files['imagen'], BUCKET, modes=('images',))
        if err:
            return jsonify({'mensaje': f'Archivo no permitido ({err})'}), 400
        imagen_name = meta['stored_name']

    nuevo = crear_anuncio({
        'titulo': titulo,
        'descripcion': descripcion,
        'imagen': imagen_name,
        'id_usuario': id_usuario
    })

    return jsonify({
        'mensaje': 'Anuncio publicado',
        'id': nuevo.id_publicacion,
        'archivo': to_archivo_obj(nuevo.imagen)
    }), 201

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['GET'])
def obtener_anuncio(id_publicacion):
    a = obtener_anuncio_por_id(id_publicacion)
    if not a:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404
    return jsonify({
        'id': a.id_publicacion,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'imagen': file_url(BUCKET, a.imagen, external=False) if a.imagen else None,
        'archivo': to_archivo_obj(a.imagen),
        'fecha_publicacion': a.fecha_publicacion.isoformat()
    })

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['PUT', 'PATCH'])
def editar_anuncio(id_publicacion):
    a = obtener_anuncio_por_id(id_publicacion)
    if not a:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404

    old = a.imagen
    titulo = request.form.get('titulo', None)
    descripcion = request.form.get('descripcion', None)
    eliminar_imagen = request.form.get('eliminar_imagen', '0') == '1'

    new_name = None
    reemplazo = False
    if 'imagen' in request.files and request.files['imagen'].filename:
        meta, err = save_upload(request.files['imagen'], BUCKET, modes=('images',))
        if err:
            return jsonify({'mensaje': f'Archivo no permitido ({err})'}), 400
        new_name = meta['stored_name']
        reemplazo = True

    # Reglas de actualización del campo imagen
    imagen_value = ('' if eliminar_imagen and not reemplazo else (new_name if reemplazo else None))
    actualizado = actualizar_anuncio(id_publicacion, titulo=titulo, descripcion=descripcion, imagen=imagen_value)

    # Borrar archivo anterior si corresponde
    if (reemplazo or eliminar_imagen) and old:
        delete_file(BUCKET, old)

    return jsonify({
        'mensaje': 'Anuncio actualizado',
        'id': actualizado.id_publicacion,
        'archivo': to_archivo_obj(actualizado.imagen)
    }), 200

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['DELETE'])
def borrar_anuncio(id_publicacion):
    a = obtener_anuncio_por_id(id_publicacion)
    if not a:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404
    old = a.imagen
    ok = eliminar_anuncio(id_publicacion)
    if not ok:
        return jsonify({'mensaje': 'No se pudo eliminar el anuncio'}), 400
    if old:
        delete_file(BUCKET, old)
    return jsonify({'mensaje': 'Anuncio eliminado', 'id': id_publicacion}), 200