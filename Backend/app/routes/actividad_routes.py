from flask import Blueprint, request, jsonify
from app.controllers.actividad_controller import (
    crear_actividad_con_archivo, listar_por_usuario, listar_todas, cambiar_estado,
    listar_aprobadas, inscribir_alumno, cancelar_inscripcion,
    listar_actividades_inscritas_por_usuario, listar_inscritos_de_actividad
)
from app.files.service import file_url
from app.utils.date_utils import format_datetime_for_frontend

actividad_bp = Blueprint('actividad', __name__)
BUCKET = 'actividades'

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

@actividad_bp.route('/actividades', methods=['POST'])
def registrar_actividad_alumno():
    res = crear_actividad_con_archivo(aprobado_por_admin=False)
    if isinstance(res, tuple):   # (json, status) en errores de validación
        return res
    return jsonify({'mensaje': 'Solicitud registrada', 'id': res.id_actividad, 'archivo': to_archivo_obj(res.archivo)}), 201

@actividad_bp.route('/actividades/admin', methods=['POST'])
def registrar_actividad_admin():
    res = crear_actividad_con_archivo(aprobado_por_admin=True)
    if isinstance(res, tuple):
        return res
    return jsonify({'mensaje': 'Actividad creada y aprobada', 'id': res.id_actividad, 'archivo': to_archivo_obj(res.archivo)}), 201

@actividad_bp.route('/actividades/usuario/<int:id_usuario>', methods=['GET'])
def ver_por_usuario(id_usuario):
    actividades = listar_por_usuario(id_usuario)
    return jsonify([{
        'id': a.id_actividad,
        'tipo': a.tipo,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'fecha_actividad': format_datetime_for_frontend(a.fecha_actividad),
        'fecha_solicitud': format_datetime_for_frontend(a.fecha_solicitud),
        'estado': a.estado,
        'archivo_obj': to_archivo_obj(a.archivo),
        'stock': a.stock,
        'motivo_cancelacion': a.motivo_cancelacion
    } for a in actividades])

@actividad_bp.route('/actividades/admin', methods=['GET'])
def ver_todas():
    actividades = listar_todas()
    return jsonify([{
        'id': a.id_actividad,
        'id_usuario': a.id_usuario,
        'nombre_usuario': a.usuario.nombre if a.usuario else None,
        'tipo': a.tipo,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'fecha_actividad': format_datetime_for_frontend(a.fecha_actividad),
        'fecha_solicitud': format_datetime_for_frontend(a.fecha_solicitud),
        'estado': a.estado,
        'motivo_cancelacion': a.motivo_cancelacion,
        'archivo_obj': to_archivo_obj(a.archivo),
        'stock': a.stock,
    } for a in actividades])

@actividad_bp.route('/actividades/<int:id_actividad>/estado', methods=['PUT'])
def actualizar_estado(id_actividad):
    data = request.get_json() or {}
    nueva = cambiar_estado(id_actividad, data.get('estado'), data.get('motivo'))
    if nueva:
        return jsonify({'mensaje': f'Estado cambiado a {nueva.estado}', 'motivo_cancelacion': nueva.motivo_cancelacion}), 200
    return jsonify({'mensaje': 'Actividad no encontrada'}), 404

@actividad_bp.route('/actividades/aprobadas', methods=['GET'])
def ver_aprobadas():
    id_usuario = request.args.get('id_usuario', type=int)
    acts = listar_aprobadas(excluir_usuario_id=id_usuario)
    resp = []
    for a in acts:
        cupos = a.stock - len(a.inscripciones)
        resp.append({
            'id': a.id_actividad,
            'titulo': a.titulo,
            'tipo': a.tipo,
            'descripcion': a.descripcion,
            'archivo_obj': to_archivo_obj(a.archivo),
            'stock': a.stock,
            'fecha_actividad': format_datetime_for_frontend(a.fecha_actividad),
            'cupos_restantes': cupos
        })
    return jsonify(resp)

@actividad_bp.route('/actividades/disponibles/<int:id_usuario>', methods=['GET'])
def ver_actividades_disponibles(id_usuario):
    """
    Obtiene todas las actividades aprobadas en las que el usuario NO está inscrito
    """
    acts = listar_aprobadas(excluir_usuario_id=id_usuario)
    resp = []
    for a in acts:
        cupos = a.stock - len(a.inscripciones)
        resp.append({
            'id': a.id_actividad,
            'titulo': a.titulo,
            'tipo': a.tipo,
            'descripcion': a.descripcion,
            'archivo_obj': to_archivo_obj(a.archivo),
            'stock': a.stock,
            'fecha_actividad': format_datetime_for_frontend(a.fecha_actividad),
            'cupos_restantes': cupos
        })
    return jsonify(resp)

@actividad_bp.route('/actividades/<int:id_actividad>/inscribirse', methods=['POST'])
def inscribirse(id_actividad):
    id_usuario = (request.json or {}).get('id_usuario')
    return inscribir_alumno(id_actividad, id_usuario)

@actividad_bp.route('/actividades/<int:id_actividad>/cancelar', methods=['DELETE'])
def desistir(id_actividad):
    id_usuario = (request.json or {}).get('id_usuario')
    return cancelar_inscripcion(id_actividad, id_usuario)

@actividad_bp.route('/actividades/inscritas/<int:id_usuario>', methods=['GET'])
def ver_inscritas_por_usuario(id_usuario):
    filas = listar_actividades_inscritas_por_usuario(id_usuario)
    return jsonify([{
        'id_inscripcion': insc.id_inscripcion,
        'fecha_registro': format_datetime_for_frontend(insc.fecha_registro),
        'id_actividad': act.id_actividad,
        'titulo': act.titulo,
        'tipo': act.tipo,
        'descripcion': act.descripcion,
        'fecha_actividad': format_datetime_for_frontend(act.fecha_actividad),
        'estado_actividad': act.estado,
        'archivo_obj': to_archivo_obj(act.archivo),
    } for (insc, act) in filas])

@actividad_bp.route('/actividades/<int:id_actividad>/inscritos', methods=['GET'])
def ver_inscritos_de_actividad(id_actividad):
    filas = listar_inscritos_de_actividad(id_actividad)
    return jsonify([{
        'id_usuario': user.id_usuario,
        'nombre': user.nombre,
        'id_inscripcion': insc.id_inscripcion,
        'fecha_registro': format_datetime_for_frontend(insc.fecha_registro)
    } for (insc, user) in filas])
