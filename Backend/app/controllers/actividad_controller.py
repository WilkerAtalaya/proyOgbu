from app.models.actividad import Actividad
from app.models.inscripcion import InscripcionActividad  
from app.models.usuarios import Usuario
from app import db
from datetime import datetime, date
from flask import request, jsonify
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'actividades'))
MAX_STOCK = 500 

from datetime import datetime, date

MAX_STOCK = 500  

def crear_actividad_con_archivo(aprobado_por_admin=False):
    #  datos del formulario 
    tipo            = request.form.get('tipo')
    titulo          = request.form.get('titulo')
    descripcion     = request.form.get('descripcion')
    fecha_raw       = request.form.get('fecha_actividad')
    stock_raw       = request.form.get('stock')          # ←  nuevo
    id_usuario      = request.form.get('id_usuario')
    archivo         = None
    # -------------------------------------------

    #  1. Validar fecha 
    try:
        fecha_actividad = datetime.strptime(fecha_raw, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return jsonify({'error': 'Formato de fecha_actividad inválido (YYYY-MM-DD)'}), 400

    if fecha_actividad < date.today():
        return jsonify({'error': 'La fecha de la actividad no puede estar en el pasado'}), 400
    # -------------------------------------------

    #  2. Validar stock 
    try:
        stock = int(stock_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Stock debe ser un número entero'}), 400

    if not (1 <= stock <= MAX_STOCK):
        return jsonify({'error': f'Stock debe estar entre 1 y {MAX_STOCK}'}), 400
    # -------------------------------------------

    #  3. Guardar archivo 
    if 'archivo' in request.files:
        archivo_file = request.files['archivo']
        if archivo_file.filename:
            filename = secure_filename(archivo_file.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            archivo_file.save(os.path.join(UPLOAD_FOLDER, filename))
            archivo = filename
    # -------------------------------------------

    nueva = Actividad(
        tipo=tipo,
        titulo=titulo,
        descripcion=descripcion,
        fecha_actividad=datetime.combine(fecha_actividad, datetime.min.time()),
        archivo=archivo,
        id_usuario=id_usuario,
        stock=stock,
        estado='Aprobado' if aprobado_por_admin else 'Pendiente'
    )
    db.session.add(nueva)
    db.session.commit()

    return nueva


def listar_por_usuario(id_usuario):
    return Actividad.query.filter_by(id_usuario=id_usuario).order_by(Actividad.fecha_solicitud.desc()).all()

def listar_todas():
    return Actividad.query.order_by(Actividad.fecha_solicitud.desc()).all()

def cambiar_estado(id_actividad, nuevo_estado):
    actividad = Actividad.query.get(id_actividad)
    if actividad:
        actividad.estado = nuevo_estado
        db.session.commit()
        return actividad
    return None

def listar_aprobadas():
    return Actividad.query.filter_by(estado='Aprobado').order_by(Actividad.fecha_solicitud.desc()).all()


def inscribir_alumno(id_actividad, id_usuario):
    actividad = Actividad.query.get(id_actividad)
    if not actividad or actividad.estado != 'Aprobado':
        return jsonify({'error': 'Actividad no encontrada o no aprobada'}), 404

    usuario = Usuario.query.get(id_usuario)
    if not usuario or usuario.rol != 'alumno':
        return jsonify({'error': 'Solo los estudiantes pueden inscribirse'}), 403

    if InscripcionActividad.query.filter_by(
            id_actividad=id_actividad, id_usuario=id_usuario).first():
        return jsonify({'error': 'Ya inscrito'}), 409

    if InscripcionActividad.query.filter_by(id_actividad=id_actividad).count() >= actividad.stock:
        return jsonify({'error': 'Cupos agotados'}), 409

    db.session.add(InscripcionActividad(id_actividad=id_actividad,
                                        id_usuario=id_usuario))
    db.session.commit()
    return jsonify({'mensaje': 'Inscripción exitosa'}), 201


def cancelar_inscripcion(id_actividad, id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario or usuario.rol != 'alumno':
        return jsonify({'error': 'Solo los estudiantes pueden cancelar'}), 403

    insc = InscripcionActividad.query.filter_by(
        id_actividad=id_actividad, id_usuario=id_usuario).first()
    if not insc:
        return jsonify({'error': 'Inscripción no encontrada'}), 404

    db.session.delete(insc)
    db.session.commit()
    return jsonify({'mensaje': 'Inscripción cancelada'}), 200
