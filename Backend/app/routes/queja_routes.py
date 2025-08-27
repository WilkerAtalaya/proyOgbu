from flask import Blueprint, request, jsonify
from app.controllers.queja_controller import (
    crear_queja, obtener_quejas_por_usuario, obtener_todas_quejas,
    actualizar_estado_queja, actualizar_queja_por_alumno
)
from datetime import datetime
from app.files.service import save_upload, delete_file, file_url
from app.models.queja import Queja
from app.utils.date_utils import format_datetime_for_frontend, parse_date_from_frontend

queja_bp = Blueprint('queja', __name__)
BUCKET = 'quejas'  

def to_archivo_obj(stored_name: str | None):
    if not stored_name:
        return None
    return {
        "bucket": BUCKET,
        "stored_name": stored_name,
        "original_name": stored_name.split('_', 1)[-1] if '_' in stored_name else stored_name,
        "size": None,  
        "mime": None,  
        "url": file_url(BUCKET, stored_name, external=True)
    } 

@queja_bp.route('/quejas', methods=['POST'])
def registrar_queja():
    asunto = request.form.get("asunto")
    motivo = request.form.get("motivo")
    descripcion = request.form.get("descripcion")
    id_usuario = request.form.get("id_usuario")

    prueba_name = None
    if 'prueba' in request.files and request.files['prueba'].filename:
        meta, err = save_upload(request.files['prueba'], BUCKET, modes=('images','docs'))
        if err:
            return jsonify({"error": f"Archivo no permitido ({err})"}), 400
        prueba_name = meta['stored_name']

    nueva = crear_queja({
        "asunto": asunto,
        "motivo": motivo,
        "descripcion": descripcion,
        "prueba": prueba_name, 
        "id_usuario": id_usuario
    })

    return jsonify({
        "mensaje": "Queja registrada",
        "codigo_reporte": nueva.codigo_reporte,
        "archivo": to_archivo_obj(nueva.prueba)
    }), 201


@queja_bp.route('/quejas/usuario/<int:id_usuario>', methods=['GET'])
def listar_quejas_usuario(id_usuario):
    quejas = obtener_quejas_por_usuario(id_usuario)
    return jsonify([{
        'codigo': q.codigo_reporte,
        'asunto': q.asunto,
        'motivo': q.motivo,
        'descripcion': q.descripcion,
        'fecha': format_datetime_for_frontend(q.fecha),
        'estado': q.estado,
        'archivo': to_archivo_obj(q.prueba)
    } for q in quejas])


@queja_bp.route('/quejas', methods=['GET'])
def listar_todas_quejas():
    estado = request.args.get('estado', type=str)
    nombre = request.args.get('nombre', type=str)
    motivo = request.args.get('motivo', type=str)

    fecha_desde_str = request.args.get('fecha_desde', type=str)
    fecha_hasta_str = request.args.get('fecha_hasta', type=str)

    fecha_desde = None
    fecha_hasta = None

    if fecha_desde_str:
        try:
            fecha_desde = parse_date_from_frontend(fecha_desde_str)
            if not fecha_desde:
                fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d')
        except ValueError:
            pass
    if fecha_hasta_str:
        try:
            fecha_hasta = parse_date_from_frontend(fecha_hasta_str)
            if not fecha_hasta:
                fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d')
        except ValueError:
            pass

    filtros = {
        'estado': estado if estado else None,
        'nombre': nombre if nombre else None,
        'motivo': motivo if motivo else None,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    }

    quejas = obtener_todas_quejas(filtros)

    quejas = obtener_todas_quejas(filtros)
    return jsonify([{
        'id': q.id_queja,
        'codigo': q.codigo_reporte,
        'asunto': q.asunto,
        'motivo': q.motivo,
        'descripcion': q.descripcion,
        'fecha': format_datetime_for_frontend(q.fecha),
        'estado': q.estado,
        'archivo': to_archivo_obj(q.prueba)   
    } for q in quejas])


@queja_bp.route('/quejas/<int:id_queja>/estado', methods=['PUT'])
def cambiar_estado_queja(id_queja):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    queja_actualizada = actualizar_estado_queja(id_queja, nuevo_estado)
    if queja_actualizada:
        return jsonify({'mensaje': 'Estado actualizado'}), 200
    return jsonify({'error': 'Queja no encontrada'}), 404


@queja_bp.route('/quejas/<int:id_queja>', methods=['PUT','PATCH'])
def editar_queja_alumno(id_queja):
    id_usuario = request.form.get('id_usuario') or request.args.get('id_usuario')
    if not id_usuario:
        return jsonify({'error': 'id_usuario es obligatorio'}), 400

    q = Queja.query.get(id_queja)
    if not q:
        return jsonify({'error': 'Queja no encontrada'}), 404
    old_file = q.prueba

    new_name = None
    reemplazo = False
    if 'prueba' in request.files and request.files['prueba'].filename:
        meta, err = save_upload(request.files['prueba'], BUCKET, modes=('images','docs'))
        if err:
            return jsonify({"error": f"Archivo no permitido ({err})"}), 400
        new_name = meta['stored_name']
        reemplazo = True

    eliminar_prueba_flag = request.form.get('eliminar_prueba', '0') == '1'
    prueba_value = ('' if eliminar_prueba_flag else (new_name if reemplazo else None))

    queja_editada, err = actualizar_queja_por_alumno(
        id_queja=id_queja,
        id_usuario=int(id_usuario),
        asunto=request.form.get('asunto'),
        motivo=request.form.get('motivo'),
        descripcion=request.form.get('descripcion'),
        prueba=prueba_value
    )
    if err == "NOT_FOUND":  return jsonify({'error': 'Queja no encontrada'}), 404
    if err == "FORBIDDEN":  return jsonify({'error': 'No puede editar una queja de otro usuario'}), 403
    if err == "LOCKED":     return jsonify({'error': 'La queja ya no es editable (estado distinto de "Recibido")'}), 409

    if (reemplazo or eliminar_prueba_flag) and old_file:
        delete_file(BUCKET, old_file)

    return jsonify({
        'mensaje': 'Queja actualizada',
        'codigo': queja_editada.codigo_reporte,
        'estado': queja_editada.estado,
        'archivo': to_archivo_obj(queja_editada.prueba)
    }), 200