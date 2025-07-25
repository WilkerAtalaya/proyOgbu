from flask import Blueprint, request, jsonify
from app.controllers.actividad_controller import crear_actividad_con_archivo, listar_por_usuario, listar_todas, cambiar_estado, listar_aprobadas, inscribir_alumno, cancelar_inscripcion

actividad_bp = Blueprint('actividad', __name__)


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
        'fecha_actividad': a.fecha_actividad.strftime('%d/%m/%Y'),
        'fecha_solicitud': a.fecha_solicitud.strftime('%d/%m/%Y'),
        'estado': a.estado,
        'archivo': a.archivo,
        'stock': a.stock,  
    } for a in actividades])

@actividad_bp.route('/actividades/admin', methods=['GET'])
def ver_todas():
    actividades = listar_todas()
    return jsonify([{
        'id': a.id_actividad,
        'usuario': a.id_usuario,
        'tipo': a.tipo,
        'titulo': a.titulo,
        'descripcion': a.descripcion,
        'fecha_actividad': a.fecha_actividad.strftime('%d/%m/%Y'),
        'fecha_solicitud': a.fecha_solicitud.strftime('%d/%m/%Y'),
        'estado': a.estado,
        'archivo': a.archivo,
        'stock': a.stock,
    } for a in actividades])

@actividad_bp.route('/actividades/<int:id_actividad>/estado', methods=['PUT'])
def actualizar_estado(id_actividad):
    data = request.get_json()
    nueva = cambiar_estado(id_actividad, data.get('estado'))
    if nueva:
        return jsonify({'mensaje': f'Estado cambiado a {nueva.estado}'})
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
            'stock': a.stock,
            'fecha_actividad': a.fecha_actividad.strftime('%d/%m/%Y'),
            'cupos_restantes': cupos
        })
    return jsonify(resp)


@actividad_bp.route('/actividades/<int:id_actividad>/inscribirse', methods=['POST'])
def inscribirse(id_actividad):
    id_usuario = request.json.get('id_usuario')
    return inscribir_alumno(id_actividad, id_usuario)

@actividad_bp.route('/actividades/<int:id_actividad>/cancelar', methods=['DELETE'])
def desistir(id_actividad):
    id_usuario = request.json.get('id_usuario')
    return cancelar_inscripcion(id_actividad, id_usuario)