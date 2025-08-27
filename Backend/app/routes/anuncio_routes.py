from flask import Blueprint, request, jsonify, g
from app.controllers.anuncio_controller import (
    crear_anuncio, obtener_anuncios, obtener_anuncio_por_id,
    actualizar_anuncio, eliminar_anuncio
)
from app.files.service import save_upload, delete_file, file_url
from app.models.usuarios import Usuario
from datetime import datetime

anuncio_bp = Blueprint('anuncio', __name__)
BUCKET = 'anuncios'

# -------------------- helpers de usuario/permisos --------------------
def _usuario_actual():
    if getattr(g, 'current_user', None):
        return g.current_user
    uid = request.headers.get('X-User-Id', type=int)
    if not uid:
        uid = request.args.get('id_usuario', type=int)
    if not uid:
        uid = request.form.get('id_usuario', type=int)
    if not uid:
        data = request.get_json(silent=True) or {}
        uid = data.get('id_usuario')
    return Usuario.query.get(uid) if uid else None

def _puede_publicar(user):
    return user and user.rol in ('admin', 'psicologia', 'social')

def _puede_editar_eliminar(user, anuncio):
    if not user or not anuncio:
        return False
    if user.rol == 'admin':
        return True
    if user.rol in ('psicologia', 'social') and anuncio.id_usuario == user.id_usuario:
        return True
    return False

def to_archivo_obj(stored_name: str | None):
    if not stored_name:
        return None
    return {
        "bucket": BUCKET,
        "stored_name": stored_name,
        "original_name": stored_name.split('_', 1)[-1] if '_' in stored_name else stored_name,
        "mime": None,
        "size": None,
        "url": file_url(BUCKET, stored_name, external=True)
    }

# -------------------- Rutas públicas --------------------
@anuncio_bp.route('/anuncios', methods=['GET'])
def listar_anuncios():
    anuncios = obtener_anuncios()
    return jsonify([{
        'id': a.id_publicacion,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'archivo': to_archivo_obj(a.imagen),
        'fecha_publicacion': a.fecha_publicacion.isoformat()
    } for a in anuncios])

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['GET'])
def obtener_anuncio(id_publicacion):
    a = obtener_anuncio_por_id(id_publicacion)
    if not a:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404
    return jsonify({
        'id': a.id_publicacion,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'archivo': to_archivo_obj(a.imagen),
        'fecha_publicacion': a.fecha_publicacion.isoformat()
    })

# -------------------- Crear / Editar / Eliminar (con permisos) --------------------
@anuncio_bp.route('/anuncios', methods=['POST'])
def publicar_anuncio():
    user = _usuario_actual()
    if not user:
        return jsonify({'mensaje': 'Usuario no identificado'}), 401
    if not _puede_publicar(user):
        return jsonify({'mensaje': 'No tiene permisos para publicar anuncios'}), 403

    titulo = (request.form.get('titulo') or '').strip()
    if not titulo:
        return jsonify({'mensaje': 'El campo "titulo" es obligatorio'}), 400
    descripcion = (request.form.get('descripcion') or '').strip()
    if not descripcion:
        return jsonify({'mensaje': 'El campo "descripcion" es obligatorio'}), 400

    stored_name = None
    upload = None
    if 'archivo' in request.files and request.files['archivo'].filename:
        upload = request.files['archivo']
    elif 'imagen' in request.files and request.files['imagen'].filename:
        upload = request.files['imagen']

    if upload:
        meta, err = save_upload(upload, BUCKET, modes=('images','docs'))
        if err:
            return jsonify({'mensaje': f'Archivo no permitido ({err})'}), 400
        stored_name = meta['stored_name']

    # id_usuario SIEMPRE es el usuario autenticado
    nuevo = crear_anuncio({
        'titulo': titulo,
        'descripcion': descripcion,
        'imagen': stored_name,
        'id_usuario': user.id_usuario
    })

    return jsonify({
        'mensaje': 'Anuncio publicado',
        'id': nuevo.id_publicacion,
        'archivo': to_archivo_obj(nuevo.imagen)
    }), 201

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['PUT', 'PATCH'])
def editar_anuncio(id_publicacion):
    user = _usuario_actual()
    if not user:
        return jsonify({'mensaje': 'Usuario no identificado'}), 401

    a = obtener_anuncio_por_id(id_publicacion)
    if not a:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404

    if not _puede_editar_eliminar(user, a):
        return jsonify({'mensaje': 'No tiene permisos para editar este anuncio'}), 403

    old = a.imagen
    titulo = request.form.get('titulo', None)
    descripcion = request.form.get('descripcion', None)
    eliminar_archivo = request.form.get('eliminar_archivo', '0') == '1' or request.form.get('eliminar_imagen', '0') == '1'

    new_name = None
    reemplazo = False

    upload = None
    if 'archivo' in request.files and request.files['archivo'].filename:
        upload = request.files['archivo']
    elif 'imagen' in request.files and request.files['imagen'].filename:
        upload = request.files['imagen']

    if upload:
        meta, err = save_upload(upload, BUCKET, modes=('images','docs'))
        if err:
            return jsonify({'mensaje': f'Archivo no permitido ({err})'}), 400
        new_name = meta['stored_name']
        reemplazo = True

    imagen_value = ('' if eliminar_archivo and not reemplazo else (new_name if reemplazo else None))
    actualizado = actualizar_anuncio(id_publicacion, titulo=titulo, descripcion=descripcion, imagen=imagen_value)

    # borrar archivo anterior si corresponde
    if (reemplazo or eliminar_archivo) and old:
        delete_file(BUCKET, old)

    return jsonify({
        'mensaje': 'Anuncio actualizado',
        'id': actualizado.id_publicacion,
        'archivo': to_archivo_obj(actualizado.imagen)
    }), 200

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['DELETE'])
def borrar_anuncio(id_publicacion):
    user = _usuario_actual()
    if not user:
        return jsonify({'mensaje': 'Usuario no identificado'}), 401

    a = obtener_anuncio_por_id(id_publicacion)
    if not a:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404

    if not _puede_editar_eliminar(user, a):
        return jsonify({'mensaje': 'No tiene permisos para eliminar este anuncio'}), 403

   
    if a.imagen:
        delete_file(BUCKET, a.imagen)
    ok = eliminar_anuncio(id_publicacion)
    if not ok:
        return jsonify({'mensaje': 'No se pudo eliminar'}), 400
    return jsonify({'mensaje': 'Anuncio eliminado'}), 200
