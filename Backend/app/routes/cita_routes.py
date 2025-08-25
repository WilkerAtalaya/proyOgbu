from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.models.usuarios import Usuario

from app.controllers.cita_controller import (
    crear_cita,
    obtener_citas_por_alumno,
    actualizar_estado_cita,
    obtener_cita,
    actualizar_citas_ausentes,
    reprogramar_cita,
    filtrar_citas, 
    ESTADOS_PENDIENTES, 
    ESTADOS_CULMINADAS
)

cita_bp = Blueprint('cita', __name__)

# -------------------- helpers de usuario --------------------
def _usuario_actual():
    if getattr(g, 'current_user', None):
        return g.current_user

    uid = request.headers.get('X-User-Id', type=int)
    if not uid:
        uid = request.args.get('id_usuario', type=int)
    if not uid:
        data = request.get_json(silent=True) or {}
        uid = data.get('id_usuario')

    return Usuario.query.get(uid) if uid else None

# -------------------- helpers de formato --------------------
def _formato_admin(c):
    return {
        'id'        : c.id_cita,
        'id_alumno' : c.id_alumno,
        'nombre'    : c.alumno.nombre,
        'motivo'    : c.motivo,
        'area'      : c.area,
        'fecha'     : c.fecha.strftime('%Y-%m-%d'),
        'horario'   : c.horario,
        'estado'    : c.estado
    }

def _extraer_filtros():
    f = {
        'id_alumno': request.args.get('id_alumno', type=int),
        'nombre'   : request.args.get('nombre'),
        'area'     : request.args.get('area'),  # ignorada para staff de área
        'fecha'    : request.args.get('fecha',
                       type=lambda d: datetime.strptime(d, '%Y-%m-%d').date() if d else None),
        # nuevos:
        'desde'    : request.args.get('desde',
                       type=lambda d: datetime.strptime(d, '%Y-%m-%d').date() if d else None),
        'hasta'    : request.args.get('hasta',
                       type=lambda d: datetime.strptime(d, '%Y-%m-%d').date() if d else None),
        'q'        : request.args.get('q')  # busca en motivo/descripcion
    }
    return {k: v for k, v in f.items() if v is not None}


# -------------------- rutas --------------------
@cita_bp.route('/citas', methods=['POST'])
def registrar_cita():
    data = (request.get_json() or {}).copy()
    # Si no vino id_usuario en el body, lo inyectamos con el usuario resuelto
    user = _usuario_actual()
    if user and 'id_usuario' not in data:
        data['id_usuario'] = user.id_usuario
    return crear_cita(data)

@cita_bp.route('/citas/alumno/<int:id_alumno>', methods=['GET'])
def ver_citas_alumno(id_alumno):
    user = _usuario_actual()
    # Candado: si es alumno, solo puede ver sus propias citas
    if user and getattr(user, 'rol', None) == 'alumno' and user.id_usuario != id_alumno:
        return jsonify({'error': 'No autorizado'}), 403

    citas = obtener_citas_por_alumno(id_alumno, user=user)
    return jsonify([{
        'id': c.id_cita,
        'motivo': c.motivo,
        'descripcion': c.descripcion,
        'area': c.area,
        'fecha': c.fecha.strftime('%Y-%m-%d'),
        'horario': c.horario,
        'estado': c.estado
    } for c in citas])

@cita_bp.route('/citas/pendientes', methods=['GET'])
def ver_pendientes():
    citas = filtrar_citas(ESTADOS_PENDIENTES, user=_usuario_actual(), **_extraer_filtros())
    return jsonify([_formato_admin(c) for c in citas])

@cita_bp.route('/citas/culminadas', methods=['GET'])
def ver_culminadas():
    citas = filtrar_citas(ESTADOS_CULMINADAS, user=_usuario_actual(), **_extraer_filtros())
    return jsonify([_formato_admin(c) for c in citas])

@cita_bp.route('/citas/<int:id_cita>/estado', methods=['PUT'])
def cambiar_estado(id_cita):
    data = request.get_json() or {}
    return actualizar_estado_cita(id_cita, data.get('estado'), user=_usuario_actual())

@cita_bp.route('/citas/<int:id_cita>', methods=['GET'])
def ver_detalle_cita(id_cita):
    c = obtener_cita(id_cita, user=_usuario_actual())
    if c:
        return jsonify({
            'id': c.id_cita,
            'nombre': c.alumno.nombre,
            'motivo': c.motivo,
            'descripcion': c.descripcion,
            'area': c.area,
            'fecha': c.fecha.strftime('%Y-%m-%d'),
            'horario': c.horario,
            'estado': c.estado
        })
    return jsonify({'error': 'No encontrada o sin permisos'}), 404

@cita_bp.route('/citas/verificar-ausentes', methods=['PUT'])
def verificar_y_actualizar_ausentes():
    return actualizar_citas_ausentes()

@cita_bp.route('/citas/<int:id_cita>/reprogramar', methods=['PUT'])
def reprogramar(id_cita):
    data = request.get_json() or {}
    try:
        nueva_fecha = datetime.strptime(data.get('fecha'), '%Y-%m-%d').date()
        nuevo_horario = data.get('horario')
        return reprogramar_cita(id_cita, nueva_fecha, nuevo_horario, user=_usuario_actual())
    except Exception:
        return jsonify({'error': 'Formato de fecha inválido o datos faltantes'}), 400