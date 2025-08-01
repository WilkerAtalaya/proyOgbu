from flask import Blueprint, request, jsonify, send_from_directory
from app.controllers.anuncio_controller import crear_anuncio, obtener_anuncios
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
            'descripcion': a.descripcion,
            'imagen': f"{request.host_url}uploads/anuncios/{a.imagen}" if a.imagen else None,
            'fecha_publicacion': a.fecha_publicacion.isoformat()
        } for a in anuncios
    ])


@anuncio_bp.route('/anuncios', methods=['POST'])
def publicar_anuncio():
    descripcion = request.form.get('descripcion')
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
        'descripcion': descripcion,
        'imagen': imagen,
        'id_usuario': id_usuario
    })

    return jsonify({'mensaje': 'Anuncio publicado', 'id': nuevo.id_publicacion}), 201


@anuncio_bp.route('/uploads/anuncios/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

