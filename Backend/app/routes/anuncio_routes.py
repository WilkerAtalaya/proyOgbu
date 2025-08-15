from flask import Blueprint, request, jsonify, send_from_directory
from app.controllers.anuncio_controller import crear_anuncio, obtener_anuncios, obtener_anuncio_por_id, actualizar_anuncio,eliminar_anuncio
from werkzeug.utils import secure_filename
import os
from datetime import datetime

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'anuncios'))
anuncio_bp = Blueprint('anuncio', __name__)


@anuncio_bp.route('/anuncios', methods=['GET'])
def listar_anuncios():
    anuncios = obtener_anuncios()
    return jsonify([
        {
            'id': a.id_publicacion,
            'titulo': a.titulo,
            'descripcion': a.descripcion,
            'imagen': f"{request.host_url}uploads/anuncios/{a.imagen}" if a.imagen else None,
            'fecha_publicacion': a.fecha_publicacion.isoformat()
        } for a in anuncios
    ])


@anuncio_bp.route('/anuncios', methods=['POST'])
def publicar_anuncio():
    titulo = (request.form.get('titulo') or '').strip()
    if not titulo:
        return jsonify({'mensaje': 'El campo "titulo" es obligatorio'}), 400

    descripcion = (request.form.get('descripcion') or '').strip()
    if not descripcion:
        return jsonify({'mensaje': 'El campo "descripcion" es obligatorio'}), 400

    id_usuario = request.form.get('id_usuario')
    imagen = None

    if 'imagen' in request.files:
        imagen_file = request.files['imagen']
        if imagen_file.filename != '':
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            filename = f"anuncio_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(imagen_file.filename)}"
            ruta = os.path.join(UPLOAD_FOLDER, filename)
            imagen_file.save(ruta)
            imagen = filename
            print("Guardando imagen en:", ruta)

    nuevo = crear_anuncio({
        'titulo': titulo,               # <-- NUEVO
        'descripcion': descripcion,
        'imagen': imagen,
        'id_usuario': id_usuario
    })

    return jsonify({'mensaje': 'Anuncio publicado', 'id': nuevo.id_publicacion}), 201


@anuncio_bp.route('/uploads/anuncios/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['GET'])
def obtener_anuncio(id_publicacion):
    anuncio = obtener_anuncio_por_id(id_publicacion)
    if not anuncio:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404

    return jsonify({
        'id': anuncio.id_publicacion,
        'titulo': anuncio.titulo,  # <-- NUEVO
        'descripcion': anuncio.descripcion,
        'imagen': f"{request.host_url}uploads/anuncios/{anuncio.imagen}" if anuncio.imagen else None,
        'fecha_publicacion': anuncio.fecha_publicacion.isoformat()
    })

@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['PUT', 'PATCH'])
def editar_anuncio(id_publicacion):
    """
    Acepta multipart/form-data para actualizar en conjunto:
      - titulo (opcional)
      - descripcion (opcional)
      - imagen (archivo opcional) -> si se envía, reemplaza la anterior
      - eliminar_imagen = "1" (opcional) -> elimina imagen sin subir nueva
    """
    anuncio = obtener_anuncio_por_id(id_publicacion)
    if not anuncio:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404

    old_image = anuncio.imagen

    # Campos opcionales
    titulo = request.form.get('titulo', None)
    descripcion = request.form.get('descripcion', None)
    eliminar_imagen_flag = request.form.get('eliminar_imagen', '0')

    new_image_name = None
    reemplazo_imagen = False

    if 'imagen' in request.files and request.files['imagen'].filename != '':
        imagen_file = request.files['imagen']
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        filename = f"anuncio_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(imagen_file.filename)}"
        ruta = os.path.join(UPLOAD_FOLDER, filename)
        imagen_file.save(ruta)
        new_image_name = filename
        reemplazo_imagen = True

    # Eliminar imagen sin subir nueva
    if eliminar_imagen_flag == '1' and not reemplazo_imagen:
        actualizado = actualizar_anuncio(id_publicacion, titulo=titulo, descripcion=descripcion, imagen='')
        if old_image:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, old_image))
            except FileNotFoundError:
                pass
        return jsonify({'mensaje': 'Anuncio actualizado (imagen eliminada)', 'id': actualizado.id_publicacion})

    # Reemplazo de imagen
    if reemplazo_imagen:
        actualizado = actualizar_anuncio(id_publicacion, titulo=titulo, descripcion=descripcion, imagen=new_image_name)
        if old_image and old_image != new_image_name:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, old_image))
            except FileNotFoundError:
                pass
        return jsonify({'mensaje': 'Anuncio actualizado', 'id': actualizado.id_publicacion})

    # Actualización solo de texto (título/descripcion)
    actualizado = actualizar_anuncio(id_publicacion, titulo=titulo, descripcion=descripcion, imagen=None)
    return jsonify({'mensaje': 'Anuncio actualizado', 'id': actualizado.id_publicacion})


@anuncio_bp.route('/anuncios/<int:id_publicacion>', methods=['DELETE'])
def borrar_anuncio(id_publicacion):
    anuncio = obtener_anuncio_por_id(id_publicacion)
    if not anuncio:
        return jsonify({'mensaje': 'Anuncio no encontrado'}), 404

    old_image = anuncio.imagen
    ok = eliminar_anuncio(id_publicacion)
    if not ok:
        return jsonify({'mensaje': 'No se pudo eliminar el anuncio'}), 400

    if old_image:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, old_image))
        except FileNotFoundError:
            pass

    return jsonify({'mensaje': 'Anuncio eliminado', 'id': id_publicacion}), 200