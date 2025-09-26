from flask import jsonify, g
from app.models.usuarios import Usuario
from app.models.rol import Rol
from app import db
from app.models.cita import Cita
from app.models.area import Area
from app.models.motivo_cita import MotivoCita
from datetime import datetime, date
from sqlalchemy import or_
from app.files.service import save_upload

# === Archivos de citas ===
BUCKET = 'citas'

# --- Constantes / roles ---
ESTADOS_PENDIENTES = ['Solicitado', 'Aprobado', 'Reprogramado']
ESTADOS_CULMINADAS = ['Atendido', 'Ausente']


# Área y motivo por defecto
AREA_POR_DEFECTO = 'Psicología'
MOTIVO_POR_DEFECTO = 'Salud Mental'

# ===== Helpers de área =====
def _area_id_por_nombre(nombre_area: str):
    if not nombre_area:
        return None
    row = db.session.query(Area.id_area).filter(Area.area == nombre_area.strip()).first()
    return row[0] if row else None

def _area_nombre_por_id(id_area: int):
    if not id_area:
        return None
    row = db.session.query(Area.area).filter(Area.id_area == id_area).first()
    return row[0] if row else None

def _area_valida_por_id(id_area: int) -> bool:
    if not id_area:
        return False
    return db.session.query(Area.id_area).filter(Area.id_area == id_area).first() is not None

def _area_id_por_motivo(motivo: str):
    """ Busca el id_area a partir del motivo en la tabla motivo_cita. """
    if not motivo:
        return None
    row = (
        db.session.query(MotivoCita.id_area)
        .filter(MotivoCita.motivo.ilike(motivo.strip()))
        .first()
    )
    return row[0] if row else None

def _obtener_area_y_motivo_por_defecto():
    """Retorna (area_id, motivo) por defecto (Psicología, Salud Mental)"""
    area_id = _area_id_por_nombre(AREA_POR_DEFECTO)
    return area_id, MOTIVO_POR_DEFECTO

# ------- Helpers de usuario/rol -------
def _get_user(user_id=None):
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user
    if user_id:
        return Usuario.query.get(user_id)
    return None

def _es_admin(user):
    return bool(user and user.rol_slug == 'admin')

def _es_alumno(user):
    return bool(user and user.rol_slug == 'alumno')

def _es_staff_area(user):
    return bool(user and user.rol_area_id)

def _area_id_del_staff(user):
    return user.rol_area_id if user else None

def _aplicar_scope_por_rol(query, user):
    # Admin ya no tiene acceso a citas
    if _es_admin(user):
        return query.filter(Cita.id_cita == -1)  # Retorna consulta vacía
    
    if _es_staff_area(user):
        area_id = _area_id_del_staff(user)
        if area_id:
            return query.filter(Cita.area_id == area_id)
    return query

def _validar_area_creacion(user, area_id_solicitada: int):
    if not _area_valida_por_id(area_id_solicitada):
        return False, 'Área inválida. Use un area_id existente'
    
    # Admin ya no puede crear citas
    if _es_admin(user):
        return False, 'El rol admin ya no tiene permisos para crear citas'
    
    if _es_staff_area(user):
        area_permitida_id = _area_id_del_staff(user)
        if area_permitida_id and area_id_solicitada != area_permitida_id:
            area_permitida = _area_nombre_por_id(area_permitida_id)
            return False, f'Como {user.rol} solo puede crear citas del área {area_permitida}'
    
    return True, None

def _puede_ver_cita(user, cita: Cita):
    # Admin ya no puede ver citas
    if _es_admin(user):
        return False
        
    if _es_staff_area(user):
        return cita.area_id == _area_id_del_staff(user)
        
    if _es_alumno(user):
        return cita.id_alumno == user.id_usuario
        
    return False

def _puede_modificar_cita(user, cita: Cita):
    if _es_admin(user):
        return False
        
    if _es_staff_area(user):
        return cita.area_id == _area_id_del_staff(user)
        
    return False  # alumnos NO modifican directo

def _actualizar_citas_vencidas():
    """Actualiza automáticamente citas aprobadas/reprogramadas cuya fecha ya pasó a estado 'Ausente'"""
    hoy = date.today()
    citas_vencidas = Cita.query.filter(
        Cita.estado.in_(['Aprobado', 'Reprogramado']),
        Cita.fecha < hoy
    ).all()
    
    if citas_vencidas:
        for cita in citas_vencidas:
            cita.estado = 'Ausente'
        db.session.commit()
        print(f"Actualizadas {len(citas_vencidas)} citas a estado 'Ausente'")


# ------------- Casos de uso ----------------
def crear_cita(data):
    # Validar campos obligatorios: fecha y horario
    if not data.get('fecha'):
        return jsonify({'error': 'La fecha es obligatoria'}), 400
    if not data.get('horario'):
        return jsonify({'error': 'El horario es obligatorio'}), 400

    try:
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
    horario = data['horario']

    # alumno obligatorio
    id_alumno = data.get('id_alumno')
    if not id_alumno:
        return jsonify({'error': 'Falta id_alumno'}), 400

    # usuario actual
    id_usuario = data.get('id_usuario')
    user = _get_user(id_usuario)
    if not user:
        return jsonify({'error': 'Usuario creador no identificado'}), 401

    # Determinar motivo y área con valores por defecto si es necesario
    motivo = data.get('motivo', '').strip()
    descripcion = data.get('descripcion', '').strip()
    area_id_solicitada = data.get('area_id')
    
    # Lógica para determinar área y motivo
    if not area_id_solicitada and not motivo:
        # Si no se proporciona área ni motivo, usar valores por defecto
        area_id, motivo = _obtener_area_y_motivo_por_defecto()
    elif area_id_solicitada and not motivo:
        # Si se proporciona área pero no motivo, mantener área y usar motivo por defecto
        area_id = area_id_solicitada
        motivo = MOTIVO_POR_DEFECTO
    elif not area_id_solicitada and motivo:
        # Si se proporciona motivo pero no área, determinar área por motivo o usar por defecto
        area_id_por_motivo = _area_id_por_motivo(motivo)
        area_id = area_id_por_motivo if area_id_por_motivo else _area_id_por_nombre(AREA_POR_DEFECTO)
    else:
        # Si se proporcionan ambos, usar los proporcionados
        area_id = area_id_solicitada

    # Validar que el área sea válida
    if not _area_valida_por_id(area_id):
        return jsonify({'error': 'Área especificada no válida'}), 400

    # Validaciones por rol/área
    ok, msg = _validar_area_creacion(user, area_id)
    if not ok:
        return jsonify({'error': msg}), 403

    # Disponibilidad (única por área_id + fecha + horario)
    # Permitir citas en mismo horario pero diferentes áreas
    ya_reservado = Cita.query.filter_by(
        fecha=fecha, 
        horario=horario, 
        area_id=area_id
    ).first()
    
    if ya_reservado:
        return jsonify({'error': 'Ese horario ya está reservado en esa área'}), 400

    # Un alumno solo una cita por día
    cita_duplicada = Cita.query.filter_by(
        id_alumno=id_alumno, 
        fecha=fecha
    ).first()
    
    if cita_duplicada:
        return jsonify({'error': 'El alumno ya tiene una cita ese día'}), 400

    nueva = Cita(
        id_alumno=id_alumno,
        motivo=motivo,
        descripcion=descripcion,
        area_id=area_id,
        fecha=fecha,
        horario=horario,
        id_usuario=id_usuario
    )

    db.session.add(nueva)
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Cita registrada exitosamente', 
        'id_cita': nueva.id_cita,
        'area_asignada': _area_nombre_por_id(area_id),
        'motivo_asignado': motivo
    }), 201

def obtener_citas_por_alumno(id_alumno, user=None):
    # Actualizar citas vencidas antes de consultar
    _actualizar_citas_vencidas()
    
    user = user or _get_user()
    q = Cita.query.filter_by(id_alumno=id_alumno).order_by(Cita.fecha_creacion.desc())
    q = _aplicar_scope_por_rol(q, user)
    return q.all()

def obtener_citas_pendientes(user=None):
    # Actualizar citas vencidas antes de consultar
    _actualizar_citas_vencidas()
    
    user = user or _get_user()
    q = Cita.query.filter(Cita.estado.in_(ESTADOS_PENDIENTES))
    q = _aplicar_scope_por_rol(q, user)
    return q.order_by(Cita.fecha_creacion.desc()).all()

def obtener_citas_culminadas(user=None):
    # Actualizar citas vencidas antes de consultar
    _actualizar_citas_vencidas()
    
    user = user or _get_user()
    q = Cita.query.filter(Cita.estado.in_(ESTADOS_CULMINADAS))
    q = _aplicar_scope_por_rol(q, user)
    return q.order_by(Cita.fecha_creacion.desc()).all()

def obtener_cita(id_cita, user=None):
    # Actualizar citas vencidas antes de consultar
    _actualizar_citas_vencidas()
    
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
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404
    if not _puede_modificar_cita(user, cita):
        return jsonify({'error': 'No tiene permisos sobre esta cita'}), 403

    ya_reservado = Cita.query.filter_by(fecha=nueva_fecha, horario=nuevo_horario, area_id=cita.area_id).first()
    if ya_reservado and ya_reservado.id_cita != id_cita:
        return jsonify({'error': 'Ese nuevo horario ya está reservado en esa área'}), 400

    otra_cita = Cita.query.filter(
        Cita.id_alumno == cita.id_alumno,
        Cita.fecha == nueva_fecha,
        Cita.id_cita != id_cita
    ).first()
    if otra_cita:
        return jsonify({'error': 'El alumno ya tiene otra cita ese día'}), 400

    cita.reprog_fecha = nueva_fecha
    cita.reprog_horario = nuevo_horario
    cita.reprog_solicitada_por = user.id_usuario
    cita.reprog_estado = 'Pendiente'
    cita.reprog_pendiente_para = 'Alumno'
    db.session.commit()
    return jsonify({'mensaje': 'Reprogramación propuesta; pendiente de confirmación del alumno'}), 200

def solicitar_reprogramacion(id_cita, nueva_fecha, nuevo_horario, user=None, motivo_txt=None):
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404

    permitido = (
        _es_admin(user) or
        (_es_staff_area(user) and cita.area_id == _area_id_del_staff(user)) or
        (_es_alumno(user) and cita.id_alumno == user.id_usuario)
    )
    if not permitido:
        return jsonify({'error': 'No tiene permisos para solicitar reprogramación'}), 403

    ocupado = Cita.query.filter_by(fecha=nueva_fecha, horario=nuevo_horario, area_id=cita.area_id).first()
    if ocupado and ocupado.id_cita != id_cita:
        return jsonify({'error': 'Horario no disponible en esa área'}), 400

    cita.reprog_fecha = nueva_fecha
    cita.reprog_horario = nuevo_horario
    cita.reprog_solicitada_por = user.id_usuario
    cita.reprog_estado = 'Pendiente'
    if _es_alumno(user):
        cita.reprog_pendiente_para = 'Staff'
        cita.reprog_motivo = (motivo_txt or '').strip() or None
    else:
        cita.reprog_pendiente_para = 'Alumno'
    db.session.commit()
    return jsonify({'mensaje': 'Reprogramación solicitada; pendiente de confirmación'}), 200

def confirmar_reprogramacion(id_cita, aceptar: bool, user=None):
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404
    if cita.reprog_estado != 'Pendiente' or not cita.reprog_fecha or not cita.reprog_horario:
        return jsonify({'error': 'No hay solicitud de reprogramación pendiente'}), 400

    if cita.reprog_pendiente_para == 'Staff':
        autorizado = _es_admin(user) or (_es_staff_area(user) and cita.area_id == _area_id_del_staff(user))
    elif cita.reprog_pendiente_para == 'Alumno':
        autorizado = _es_alumno(user) and user.id_usuario == cita.id_alumno
    else:
        autorizado = False

    if not autorizado:
        return jsonify({'error': 'No tiene permisos para confirmar esta reprogramación'}), 403

    if aceptar:
        ocupado = Cita.query.filter_by(fecha=cita.reprog_fecha, horario=cita.reprog_horario, area_id=cita.area_id).first()
        if ocupado and ocupado.id_cita != id_cita:
            return jsonify({'error': 'Horario no disponible en esa área'}), 400

        cita.fecha = cita.reprog_fecha
        cita.horario = cita.reprog_horario
        cita.estado = 'Aprobado'
        cita.reprog_estado = 'Aceptada'
    else:
        cita.reprog_estado = 'Rechazada'

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
def agenda_publica(area=None, fecha=None, area_id=None):

    # Normalizar área -> obtener _area_id
    _area_id = None
    if area_id:
        if not _area_valida_por_id(area_id):
            return jsonify({'error': 'area_id inválido'}), 400
        _area_id = area_id
    elif area:
        _area_id = _area_id_por_nombre(area)
        if not _area_id:
            return jsonify({'error': 'Área inválida'}), 400

    # Base: estados permitidos
    q = Cita.query.filter(Cita.estado.in_(['Aprobado', 'Reprogramado']))

    # Fecha opcional
    if fecha:
        q = q.filter(Cita.fecha == fecha)
    else:
        q = q.filter(Cita.fecha >= date.today())

    # Área opcional
    if _area_id:
        q = q.filter(Cita.area_id == _area_id)

    # Orden
    if fecha:
        q = q.order_by(Cita.horario.asc())
    else:
        q = q.order_by(Cita.fecha.asc(), Cita.horario.asc())

    items = q.all()
    data = [{
        'fecha': c.fecha.strftime('%Y-%m-%d'),
        'horario': c.horario,
        'area_id': c.area_id,
        'area': c.area_rel.area if c.area_rel else None,
        'disponible': False
    } for c in items]

    return jsonify(data), 200

def filtrar_citas(estado_lista, user=None, **filtros):
    # Actualizar citas vencidas antes de consultar
    _actualizar_citas_vencidas()
    
    user = user or _get_user()
    consulta = Cita.query.join(Cita.alumno).join(Cita.area_rel).filter(Cita.estado.in_(estado_lista))

    # Rol/área
    if _es_staff_area(user):
        consulta = consulta.filter(Cita.area_id == _area_id_del_staff(user))
    else:
        # filtros por área: aceptar area_id o area (texto)
        if filtros.get('area_id'):
            consulta = consulta.filter(Cita.area_id == filtros['area_id'])
        elif filtros.get('area'):
            a_id = _area_id_por_nombre(filtros['area'])
            if a_id:
                consulta = consulta.filter(Cita.area_id == a_id)

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

    # Siempre ordenar por fecha de creación descendente (más reciente primero)
    consulta = consulta.order_by(Cita.fecha_creacion.desc())

    return consulta.all()