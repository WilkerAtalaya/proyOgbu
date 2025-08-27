from flask import jsonify, g
from app.models.usuarios import Usuario
from app import db
from app.models.cita import Cita
from datetime import datetime
from sqlalchemy import or_
from app.files.service import save_upload  # usamos el servicio, pero el BUCKET vive aquí

# === Archivos de citas ===
BUCKET = 'citas'

# --- Constantes / roles ---
ROLES = ('alumno', 'admin', 'psicologia', 'social')
AREAS = ('Psicología', 'Trabajo Social')
ESTADOS_PENDIENTES  = ['Solicitado', 'Aprobado', 'Reprogramado']
ESTADOS_CULMINADAS  = ['Atendido', 'Ausente']

ROL_A_AREA = {
    'psicologia': 'Psicología',
    'social': 'Trabajo Social',
}

# Mapeo motivo -> área
MOTIVO_A_AREA = {
    'Salud Mental': 'Psicología',
    'Rendimiento Académico': 'Trabajo Social',
    'Psicosocial': 'Trabajo Social',
}

def _area_por_motivo(motivo: str):
    if not motivo:
        return None
    return MOTIVO_A_AREA.get(motivo.strip())

# ------- Helpers -------
def _get_user(user_id=None):
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user
    if user_id:
        return Usuario.query.get(user_id)
    return None

def _es_admin(user):
    return user and user.rol == 'admin'

def _es_alumno(user):
    return user and user.rol == 'alumno'

def _es_staff_area(user):
    return user and user.rol in ROL_A_AREA

def _area_del_staff(user):
    return ROL_A_AREA.get(user.rol)

def _aplicar_scope_por_rol(query, user):
    if _es_staff_area(user):
        return query.filter(Cita.area == _area_del_staff(user))
    return query

def _validar_area_creacion(user, area_solicitada):
    if area_solicitada not in AREAS:
        return False, 'Área inválida. Use: Psicología o Trabajo Social'
    if _es_staff_area(user):
        area_permitida = _area_del_staff(user)
        if area_solicitada != area_permitida:
            return False, f'Como {user.rol} solo puede crear citas del área {area_permitida}'
    return True, None

def _puede_ver_cita(user, cita: Cita):
    if _es_admin(user):
        return True
    if _es_staff_area(user):
        return cita.area == _area_del_staff(user)
    if _es_alumno(user):
        return cita.id_alumno == user.id_usuario
    return False

def _puede_modificar_cita(user, cita: Cita):
    if _es_admin(user):
        return True
    if _es_staff_area(user):
        return cita.area == _area_del_staff(user)
    return False  # alumnos NO modifican directo

# ------------- Casos de uso ----------------
def crear_cita(data):
    fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    horario = data['horario']

    id_alumno = data.get('id_alumno')
    if not id_alumno:
        return jsonify({'error': 'Falta id_alumno'}), 400

    id_usuario = data.get('id_usuario')  # quien registra (admin/alumno/staff)
    user = _get_user(id_usuario)
    if not user:
        return jsonify({'error': 'Usuario creador no identificado'}), 401

    # motivo/descripcion
    if _es_alumno(user):
        motivo = data.get('motivo', 'Salud Mental')      # el alumno puede enviarlo
        descripcion = None
    else:
        motivo = data.get('motivo', 'Salud Mental')
        descripcion = data.get('descripcion')

    # área por motivo
    area_motivo = _area_por_motivo(motivo)
    area_req = data.get('area')

    if area_motivo:
        area = area_motivo
        if area_req and area_req != area_motivo:
            return jsonify({'error': f"Área inconsistente con el motivo. Para '{motivo}' el área debe ser '{area_motivo}'."}), 400
    else:
        if not area_req:
            return jsonify({'error': 'Área requerida o motivo no reconocido para asignar área'}), 400
        area = area_req

    # Validaciones
    ok, msg = _validar_area_creacion(user, area)
    if not ok:
        return jsonify({'error': msg}), 403

    ya_reservado = Cita.query.filter_by(fecha=fecha, horario=horario, area=area).first()
    if ya_reservado:
        return jsonify({'error': 'Ese horario ya está reservado en esa área'}), 400

    cita_duplicada = Cita.query.filter_by(id_alumno=id_alumno, fecha=fecha).first()
    if cita_duplicada:
        return jsonify({'error': 'El alumno ya tiene una cita ese día'}), 400

    nueva = Cita(
        id_alumno=id_alumno,
        motivo=motivo,
        descripcion=descripcion,
        area=area,
        fecha=fecha,
        horario=horario,
        id_usuario=id_usuario
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({'mensaje': 'Cita registrada exitosamente', 'id_cita': nueva.id_cita}), 201

def obtener_citas_por_alumno(id_alumno, user=None):
    user = user or _get_user()
    q = Cita.query.filter_by(id_alumno=id_alumno).order_by(Cita.fecha.desc())
    q = _aplicar_scope_por_rol(q, user)
    return q.all()

def obtener_citas_pendientes(user=None):
    user = user or _get_user()
    q = Cita.query.filter(Cita.estado.in_(ESTADOS_PENDIENTES))
    q = _aplicar_scope_por_rol(q, user)
    return q.order_by(Cita.fecha.asc(), Cita.horario.asc()).all()

def obtener_citas_culminadas(user=None):
    user = user or _get_user()
    q = Cita.query.filter(Cita.estado.in_(ESTADOS_CULMINADAS))
    q = _aplicar_scope_por_rol(q, user)
    return q.order_by(Cita.fecha.desc(), Cita.horario.asc()).all()

def obtener_cita(id_cita, user=None):
    user = user or _get_user()
    c = Cita.query.get(id_cita)
    if c and _puede_ver_cita(user, c):
        return c
    return None

def actualizar_estado_cita(id_cita, nuevo_estado, user=None):
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404
    if not _puede_modificar_cita(user, cita):
        return jsonify({'error': 'No tiene permisos sobre esta cita'}), 403

    cita.estado = nuevo_estado
    db.session.commit()
    return jsonify({'mensaje': 'Estado actualizado'}), 200

# ---------------- Reprogramación ----------------
def reprogramar_cita(id_cita, nueva_fecha, nuevo_horario, user=None):
    """
    Propuesta de reprogramación hecha por admin/staff.
    En vez de aplicar directo, se crea una solicitud PENDIENTE para que la confirme el ALUMNO.
    (El staff no debe dar ni motivo ni adjuntar archivos).
    """
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404
    if not _puede_modificar_cita(user, cita):
        return jsonify({'error': 'No tiene permisos sobre esta cita'}), 403

    ya_reservado = Cita.query.filter_by(fecha=nueva_fecha, horario=nuevo_horario, area=cita.area).first()
    if ya_reservado and ya_reservado.id_cita != id_cita:
        return jsonify({'error': 'Ese nuevo horario ya está reservado en esa área'}), 400

    otra_cita = Cita.query.filter(
        Cita.id_alumno == cita.id_alumno,
        Cita.fecha == nueva_fecha,
        Cita.id_cita != id_cita
    ).first()
    if otra_cita:
        return jsonify({'error': 'El alumno ya tiene otra cita ese día'}), 400

    # Propuesta para el Alumno
    cita.reprog_fecha = nueva_fecha
    cita.reprog_horario = nuevo_horario
    cita.reprog_solicitada_por = user.id_usuario
    cita.reprog_estado = 'Pendiente'
    cita.reprog_pendiente_para = 'Alumno'
    # No se tocan reprog_motivo / reprog_evid_* (solo alumno)

    db.session.commit()
    return jsonify({'mensaje': 'Reprogramación propuesta; pendiente de confirmación del alumno'}), 200

def solicitar_reprogramacion(id_cita, nueva_fecha, nuevo_horario, user=None, motivo_txt=None):
    """
    Alumno o staff piden cambio; queda Pendiente hasta que CONFIRME
    el destinatario correcto (Alumno o Staff).
    - Si quien solicita es ALUMNO → puede incluir 'motivo' y luego adjuntar evidencia en un endpoint aparte.
    """
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404

    permitido = (
        _es_admin(user)
        or (_es_staff_area(user) and cita.area == _area_del_staff(user))
        or (_es_alumno(user) and cita.id_alumno == user.id_usuario)
    )
    if not permitido:
        return jsonify({'error': 'No tiene permisos para solicitar reprogramación'}), 403

    ocupado = Cita.query.filter_by(fecha=nueva_fecha, horario=nuevo_horario, area=cita.area).first()
    if ocupado and ocupado.id_cita != id_cita:
        return jsonify({'error': 'Horario no disponible en esa área'}), 400

    cita.reprog_fecha = nueva_fecha
    cita.reprog_horario = nuevo_horario
    cita.reprog_solicitada_por = user.id_usuario
    cita.reprog_estado = 'Pendiente'

    if _es_alumno(user):
        cita.reprog_pendiente_para = 'Staff'
        # Guardar motivo solo si lo envía el alumno
        cita.reprog_motivo = (motivo_txt or '').strip() or None
    else:
        cita.reprog_pendiente_para = 'Alumno'
        # Staff no guarda motivo/evidencia

    db.session.commit()
    return jsonify({'mensaje': 'Reprogramación solicitada; pendiente de confirmación'}), 200

def confirmar_reprogramacion(id_cita, aceptar: bool, user=None):
    """
    Confirma/rechaza la solicitud de reprogramación.
    - Si la propuesta está 'pendiente para' Staff → confirman admin/staff del área.
    - Si está 'pendiente para' Alumno → confirma el alumno titular.
    Al aceptar: estado pasa a 'Aprobado'. Se limpian campos temporales.
    """
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404

    if cita.reprog_estado != 'Pendiente' or not cita.reprog_fecha or not cita.reprog_horario:
        return jsonify({'error': 'No hay solicitud de reprogramación pendiente'}), 400

    # ¿Quién confirma?
    if cita.reprog_pendiente_para == 'Staff':
        autorizado = _es_admin(user) or (_es_staff_area(user) and cita.area == _area_del_staff(user))
    elif cita.reprog_pendiente_para == 'Alumno':
        autorizado = _es_alumno(user) and user.id_usuario == cita.id_alumno
    else:
        autorizado = False

    if not autorizado:
        return jsonify({'error': 'No tiene permisos para confirmar esta reprogramación'}), 403

    if aceptar:
        # Validación final de disponibilidad
        ocupado = Cita.query.filter_by(fecha=cita.reprog_fecha, horario=cita.reprog_horario, area=cita.area).first()
        if ocupado and ocupado.id_cita != id_cita:
            return jsonify({'error': 'Horario no disponible en esa área'}), 400

        cita.fecha = cita.reprog_fecha
        cita.horario = cita.reprog_horario
        cita.estado = 'Aprobado'
        cita.reprog_estado = 'Aceptada'
    else:
        cita.reprog_estado = 'Rechazada'

    # Limpiar propuesta/argumentos
    cita.reprog_fecha = None
    cita.reprog_horario = None
    cita.reprog_solicitada_por = None
    cita.reprog_pendiente_para = None
    cita.reprog_motivo = None
    cita.reprog_evid_bucket = None
    cita.reprog_evid_name = None

    db.session.commit()
    return jsonify({'mensaje': 'Reprogramación confirmada' if aceptar else 'Solicitud rechazada'}), 200

# --------- Upload de evidencia (solo alumno) ----------
def adjuntar_evidencia_reprog(id_cita, file_storage, user=None):
    """
    Sube un archivo de evidencia para una solicitud de reprogramación.
    - Solo el ALUMNO titular puede adjuntar.
    - Guarda en uploads/citas (BUCKET = 'citas').
    """
    user = user or _get_user()
    if not user:
        return jsonify({'error': 'Usuario no identificado'}), 401
    if not _es_alumno(user):
        return jsonify({'error': 'Solo el alumno puede adjuntar evidencia'}), 403

    cita = Cita.query.get(id_cita)
    if not cita or cita.id_alumno != user.id_usuario:
        return jsonify({'error': 'Cita no encontrada o no pertenece al alumno'}), 404

    if not file_storage or not file_storage.filename:
        return jsonify({'error': 'Archivo requerido (campo "file")'}), 400

    meta, err = save_upload(file_storage, BUCKET, modes=('images','docs'))
    if err == "INVALID_EXT":
        return jsonify({'error': 'Extensión no permitida'}), 400
    if err == "TOO_LARGE":
        return jsonify({'error': 'Archivo demasiado grande (máx 10 MB)'}), 400
    if err:
        return jsonify({'error': f'No se pudo guardar el archivo ({err})'}), 400

    cita.reprog_evid_bucket = meta['bucket']
    cita.reprog_evid_name = meta['stored_name']
    db.session.commit()

    return jsonify({'mensaje': 'Evidencia cargada', 'url': meta['url']}), 201

# --------- Agenda pública (anonimizada) ----------
def agenda_publica(area, desde, hasta):
    """
    Devuelve SOLO slots ocupados (Aprobado/Reprogramado) sin datos personales.
    Las solicitudes PENDIENTES NO bloquean agenda pública.
    """
    if area not in AREAS:
        return jsonify({'error': 'Área inválida. Use: Psicología o Trabajo Social'}), 400
    q = (Cita.query
         .filter(Cita.area == area,
                 Cita.estado.in_(['Aprobado', 'Reprogramado']),
                 Cita.fecha >= desde,
                 Cita.fecha <= hasta)
         .order_by(Cita.fecha.asc(), Cita.horario.asc())
         .all())
    data = [{'fecha': c.fecha.strftime('%Y-%m-%d'),
             'horario': c.horario,
             'disponible': False} for c in q]
    return jsonify(data), 200

def filtrar_citas(estado_lista, user=None, **filtros):
    user = user or _get_user()
    consulta = Cita.query.join(Cita.alumno).filter(Cita.estado.in_(estado_lista))

    if _es_staff_area(user):
        consulta = consulta.filter(Cita.area == _area_del_staff(user))
    elif filtros.get('area'):
        consulta = consulta.filter(Cita.area == filtros['area'])

    if filtros.get('id_alumno'):
        consulta = consulta.filter(Cita.id_alumno == filtros['id_alumno'])

    if filtros.get('nombre'):
        patron = f"%{filtros['nombre']}%"
        consulta = consulta.filter(Usuario.nombre.ilike(patron))

    if filtros.get('fecha'):
        consulta = consulta.filter(Cita.fecha == filtros['fecha'])

    if filtros.get('desde'):
        consulta = consulta.filter(Cita.fecha >= filtros['desde'])
    if filtros.get('hasta'):
        consulta = consulta.filter(Cita.fecha <= filtros['hasta'])
    if filtros.get('q'):
        p = f"%{filtros['q']}%"
        consulta = consulta.filter(or_(Cita.motivo.ilike(p), Cita.descripcion.ilike(p)))

    if estado_lista == ESTADOS_PENDIENTES:
        consulta = consulta.order_by(Cita.fecha.asc(), Cita.horario.asc())
    else:
        consulta = consulta.order_by(Cita.fecha.desc(), Cita.horario.asc())
    return consulta.all()
