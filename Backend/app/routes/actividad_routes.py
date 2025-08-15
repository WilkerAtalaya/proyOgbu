from flask import Blueprint, request, jsonify, send_from_directory
from app.controllers.actividad_controller import crear_actividad_con_archivo, listar_por_usuario, listar_todas, cambiar_estado, listar_aprobadas, inscribir_alumno, cancelar_inscripcion, listar_actividades_inscritas_por_usuario, listar_inscritos_de_actividad, UPLOAD_FOLDER

actividad_bp = Blueprint('actividad', __name__)

@actividad_bp.route('/uploads/actividades/<path:filename>', methods=['GET'])
def serve_actividad_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@actividad_bp.route('/actividades', methods=['POST'])
def registrar_actividad_alumno():
    resultado = crear_actividad_con_archivo(aprobado_por_admin=False)
    
    if isinstance(resultado, tuple):
        return resultado

    return jsonify({'mensaje': 'Solicitud registrada', 'id': resultado.id_actividad}), 201


@actividad_bp.route('/actividades/admin', methods=['POST'])
def registrar_actividad_admin():
    resultado = crear_actividad_con_archivo(aprobado_por_admin=True)
    
    if isinstance(resultado, tuple):
        return resultado

    return jsonify({'mensaje': 'Actividad creada y aprobada', 'id': resultado.id_actividad}), 201



@actividad_bp.route('/actividades/usuario/<int:id_usuario>', methods=['GET'])
def ver_por_usuario(id_usuario):
    actividades = listar_por_usuario(id_usuario)
    return jsonify([{
        'id': a.id_actividad,
        'tipo': a.tipo,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'fecha_actividad': a.fecha_actividad.isoformat(),  
        'fecha_solicitud': a.fecha_solicitud.isoformat(),  
        'estado': a.estado,
        'archivo': f"{request.host_url}uploads/actividades/{a.archivo}" if a.archivo else None,
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
        'fecha_actividad': a.fecha_actividad.isoformat(),
        'fecha_solicitud': a.fecha_solicitud.isoformat(), 
        'estado': a.estado,
        'motivo_cancelacion': a.motivo_cancelacion,
        'archivo': f"{request.host_url}uploads/actividades/{a.archivo}" if a.archivo else None,
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
    acts = listar_aprobadas()
    resp = []
    for a in acts:
        cupos = a.stock - len(a.inscripciones)
        resp.append({
            'id': a.id_actividad,
            'titulo': a.titulo,
            'tipo': a.tipo,
            'descripcion': a.descripcion,
            'archivo': f"{request.host_url}uploads/actividades/{a.archivo}" if a.archivo else None,
            'stock': a.stock,
            'fecha_actividad': a.fecha_actividad.isoformat(),
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
        'fecha_registro': insc.fecha_registro.isoformat(),  
        'id_actividad': act.id_actividad,
        'titulo': act.titulo,
        'tipo': act.tipo,
        'descripcion': act.descripcion,
        'fecha_actividad': act.fecha_actividad.isoformat(), 
        'estado_actividad': act.estado,
        'archivo': f"{request.host_url}uploads/actividades/{act.archivo}" if act.archivo else None
    } for (insc, act) in filas])

@actividad_bp.route('/actividades/<int:id_actividad>/inscritos', methods=['GET'])
def ver_inscritos_de_actividad(id_actividad):
    filas = listar_inscritos_de_actividad(id_actividad)
    return jsonify([{
        'id_usuario': user.id_usuario,
        'nombre': user.nombre,
        'id_inscripcion': insc.id_inscripcion,
        'fecha_registro': insc.fecha_registro.isoformat()  
    } for (insc, user) in filas])

