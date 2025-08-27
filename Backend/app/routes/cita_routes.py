from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.models.usuarios import Usuario

from app.controllers.cita_controller import (
    crear_cita,
    actualizar_estado_cita,
    obtener_cita,
    obtener_citas_por_alumno,
    filtrar_citas,
    reprogramar_cita,
    solicitar_reprogramacion,
    confirmar_reprogramacion,
    agenda_publica,
    ESTADOS_PENDIENTES,
    ESTADOS_CULMINADAS,
    adjuntar_evidencia_reprog,   # << nuevo
)
from app.files.service import file_url  # solo para construir URLs en respuestas

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
        'id_alumno' : request.args.get('id_alumno', type=int),
        'nombre'    : request.args.get('nombre'),
        'area'      : request.args.get('area'),
        'fecha'     : request.args.get('fecha',
                       type=lambda d: datetime.strptime(d, '%Y-%m-%d').date() if d else None),
        'desde'     : request.args.get('desde',
                       type=lambda d: datetime.strptime(d, '%Y-%m-%d').date() if d else None),
        'hasta'     : request.args.get('hasta',
                       type=lambda d: datetime.strptime(d, '%Y-%m-%d').date() if d else None),
        'q'         : request.args.get('q')
    }
    return {k: v for k, v in f.items() if v is not None}

# -------------------- rutas --------------------
@cita_bp.route('/citas', methods=['POST'])
def registrar_cita():
    data = (request.get_json() or {}).copy()
    user = _usuario_actual()
    if user and 'id_usuario' not in data:
        data['id_usuario'] = user.id_usuario
    # autocompletar id_alumno si el que crea es alumno
    if user and getattr(user, 'rol', None) == 'alumno' and 'id_alumno' not in data:
        data['id_alumno'] = user.id_usuario
    return crear_cita(data)

@cita_bp.route('/citas/alumno/<int:id_alumno>', methods=['GET'])
def ver_citas_alumno(id_alumno):
    user = _usuario_actual()
    if user and getattr(user, 'rol', None) == 'alumno' and user.id_usuario != id_alumno:
        return jsonify({'error': 'No autorizado'}), 403

    citas = obtener_citas_por_alumno(id_alumno, user=user)
    return jsonify([{
        'id'        : c.id_cita,
        'id_alumno' : c.id_alumno,
        'motivo'    : c.motivo,
        'descripcion': c.descripcion,
        'area'      : c.area,
        'fecha'     : c.fecha.strftime('%Y-%m-%d'),
        'horario'   : c.horario,
        'estado'    : c.estado,
        'reprog': {
            'estado': c.reprog_estado,
            'pendiente_para': c.reprog_pendiente_para,
            'motivo': c.reprog_motivo,
            'evidencia_url': file_url(c.reprog_evid_bucket, c.reprog_evid_name) if c.reprog_evid_name else None
        }
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
    user = _usuario_actual()
    if not user:
        return jsonify({'error': 'Usuario no identificado'}), 401
    data = request.get_json() or {}
    return actualizar_estado_cita(id_cita, data.get('estado'), user=user)

@cita_bp.route('/citas/<int:id_cita>', methods=['GET'])
def ver_detalle_cita(id_cita):
    c = obtener_cita(id_cita, user=_usuario_actual())
    if c:
        return jsonify({
            'id'        : c.id_cita,
            'id_alumno' : c.id_alumno,
            'nombre'    : c.alumno.nombre,
            'motivo'    : c.motivo,
            'descripcion': c.descripcion,
            'area'      : c.area,
            'fecha'     : c.fecha.strftime('%Y-%m-%d'),
            'horario'   : c.horario,
            'estado'    : c.estado,
            'reprog': {
                'estado': c.reprog_estado,
                'pendiente_para': c.reprog_pendiente_para,
                'motivo': c.reprog_motivo,
                'evidencia_url': file_url(c.reprog_evid_bucket, c.reprog_evid_name) if c.reprog_evid_name else None
            }
        })
    return jsonify({'error': 'No encontrada o sin permisos'}), 404

# Reprogramación por staff (crea propuesta al Alumno)
@cita_bp.route('/citas/<int:id_cita>/reprogramar', methods=['PUT'])
def reprogramar(id_cita):
    user = _usuario_actual()
    if not user:
        return jsonify({'error': 'Usuario no identificado'}), 401
    data = request.get_json() or {}
    try:
        nueva_fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'fecha inválida (YYYY-MM-DD)'}), 400
    nuevo_horario = data.get('horario')
    if not nuevo_horario:
        return jsonify({'error': 'horario es requerido'}), 400
    return reprogramar_cita(id_cita, nueva_fecha, nuevo_horario, user=user)

# Handshake: alumno/staff solicitan reprogramación (el alumno puede añadir motivo)
@cita_bp.route('/citas/<int:id_cita>/reprogramacion/solicitar', methods=['PUT'])
def solicitar_reprog(id_cita):
    user = _usuario_actual()
    if not user:
        return jsonify({'error': 'Usuario no identificado'}), 401
    data = request.get_json() or {}
    try:
        nueva_fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'fecha inválida (YYYY-MM-DD)'}), 400
    nuevo_horario = data.get('horario')
    if not nuevo_horario:
        return jsonify({'error': 'horario es requerido'}), 400

    motivo_txt = (data.get('motivo') or '').strip() if getattr(user, 'rol', None) == 'alumno' else None
    return solicitar_reprogramacion(id_cita, nueva_fecha, nuevo_horario, user=user, motivo_txt=motivo_txt)

@cita_bp.route('/citas/<int:id_cita>/reprogramacion/confirmar', methods=['PUT'])
def confirmar_reprog(id_cita):
    user = _usuario_actual()
    if not user:
        return jsonify({'error': 'Usuario no identificado'}), 401
    data = request.get_json() or {}
    aceptar = bool(data.get('aceptar', True))
    return confirmar_reprogramacion(id_cita, aceptar, user=user)

# Solo ALUMNO: subir evidencia (archivo) para la reprogramación
@cita_bp.route('/citas/<int:id_cita>/reprogramacion/evidencia', methods=['POST'])
def subir_evidencia_reprog_route(id_cita):
    user = _usuario_actual()
    if not user:
        return jsonify({'error': 'Usuario no identificado'}), 401
    # archivo en form-data con key 'file'
    file = request.files.get('file')
    return adjuntar_evidencia_reprog(id_cita, file, user=user)

# Agenda pública anonimizada
@cita_bp.route('/citas/agenda-publica', methods=['GET'])
def ver_agenda_publica():
    # Todos los filtros son OPCIONALES
    area = request.args.get('area')  # 'Psicología' | 'Trabajo Social' | None

    # Parseo opcional de fechas
    def _to_date(s):
        try:
            return datetime.strptime(s, '%Y-%m-%d').date() if s else None
        except Exception:
            return None

    desde = _to_date(request.args.get('desde'))
    hasta = _to_date(request.args.get('hasta'))

    # Si enviaron una fecha con formato inválido, devolvemos 400
    if request.args.get('desde') and not desde:
        return jsonify({'error': 'desde inválida (use YYYY-MM-DD)'}), 400
    if request.args.get('hasta') and not hasta:
        return jsonify({'error': 'hasta inválida (use YYYY-MM-DD)'}), 400

    return agenda_publica(area=area, desde=desde, hasta=hasta)
