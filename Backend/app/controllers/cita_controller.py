from flask import jsonify, g
from app.models.usuarios import Usuario
from app import db
from app.models.cita import Cita
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy import or_

# --- Constantes de dominio ---
ROLES = ('alumno', 'admin', 'psicologia', 'social')
AREAS = ('Psicología', 'Trabajo Social')
ESTADOS_PENDIENTES  = ['Solicitado', 'Aprobado', 'Reprogramado']
ESTADOS_CULMINADAS  = ['Atendido', 'Ausente']

# Mapea rol -> área que puede ver/crear
ROL_A_AREA = {
    'psicologia': 'Psicología',
    'social': 'Trabajo Social',
}

# ------- Helpers de autorización / scoping 
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
    # alumno y admin pueden cualquier área
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
    # alumnos NO pueden modificar
    return False


# ------------- Casos de uso ----------------
def crear_cita(data):
    fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    horario = data['horario']
    id_alumno = data['id_alumno']
    id_usuario = data.get('id_usuario')  # admin o el mismo alumno
    area = data['area']

    user = _get_user(id_usuario)
    if not user:
        return jsonify({'error': 'Usuario creador no identificado'}), 401

    ok, msg = _validar_area_creacion(user, area)
    if not ok:
        return jsonify({'error': msg}), 403

    # Validar que no haya cruce de horarios (por fecha y horario)
    ya_reservado = Cita.query.filter_by(fecha=fecha, horario=horario, area=area).first()
    if ya_reservado:
        return jsonify({'error': 'Ese horario ya está reservado en esa área'}), 400

    # Validar que el alumno no tenga otra cita el mismo día (independiente del área)
    cita_duplicada = Cita.query.filter_by(id_alumno=id_alumno, fecha=fecha).first()
    if cita_duplicada:
        return jsonify({'error': 'El alumno ya tiene una cita ese día'}), 400

    nueva = Cita(
        id_alumno=id_alumno,
        motivo=data['motivo'],
        descripcion=data['descripcion'],
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
    q = _aplicar_scope_por_rol(q, user)  # si es staff, solo su área
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

def actualizar_citas_ausentes():
    ahora = datetime.now()
    citas = Cita.query.filter(Cita.estado.in_(ESTADOS_PENDIENTES)).all()
    cambios = 0
    for cita in citas:
        fin = datetime.strptime(cita.horario.split(' - ')[1], "%I:%M%p").time()
        cita_datetime = datetime.combine(cita.fecha, fin)
        if ahora > cita_datetime:
            cita.estado = 'Ausente'
            cambios += 1
    if cambios:
        db.session.commit()
    return cambios

def reprogramar_cita(id_cita, nueva_fecha, nuevo_horario, user=None):
    user = user or _get_user()
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404
    if not _puede_modificar_cita(user, cita):
        return jsonify({'error': 'No tiene permisos sobre esta cita'}), 403

    # Validar si ese nuevo horario ya está reservado en esa área
    ya_reservado = Cita.query.filter_by(fecha=nueva_fecha, horario=nuevo_horario, area=cita.area).first()
    if ya_reservado and ya_reservado.id_cita != id_cita:
        return jsonify({'error': 'Ese nuevo horario ya está reservado en esa área'}), 400

    # Validar si el alumno ya tiene otra cita ese mismo día (excepto esta)
    otra_cita = Cita.query.filter(
        Cita.id_alumno == cita.id_alumno,
        Cita.fecha == nueva_fecha,
        Cita.id_cita != id_cita
    ).first()
    if otra_cita:
        return jsonify({'error': 'El alumno ya tiene otra cita ese día'}), 400

    cita.fecha = nueva_fecha
    cita.horario = nuevo_horario
    cita.estado = 'Reprogramado'
    db.session.commit()

    return jsonify({'mensaje': 'Cita reprogramada correctamente'}), 200

def filtrar_citas(estado_lista, user=None, **filtros):
    user = user or _get_user()
    consulta = Cita.query.join(Cita.alumno).filter(Cita.estado.in_(estado_lista))

    # Scope por rol: psicologia/social quedan forzados a su propia área
    if _es_staff_area(user):
        consulta = consulta.filter(Cita.area == _area_del_staff(user))
    elif filtros.get('area'):
        # admin (u otros) pueden filtrar por área
        consulta = consulta.filter(Cita.area == filtros['area'])

    if filtros.get('id_alumno'):
        consulta = consulta.filter(Cita.id_alumno == filtros['id_alumno'])

    if filtros.get('nombre'):
        patron = f"%{filtros['nombre']}%"
        consulta = consulta.filter(Usuario.nombre.ilike(patron))

    if filtros.get('fecha'):
        consulta = consulta.filter(Cita.fecha == filtros['fecha'])

    # nuevos filtros
    if filtros.get('desde'):
        consulta = consulta.filter(Cita.fecha >= filtros['desde'])
    if filtros.get('hasta'):
        consulta = consulta.filter(Cita.fecha <= filtros['hasta'])
    if filtros.get('q'):
        p = f"%{filtros['q']}%"
        consulta = consulta.filter(or_(Cita.motivo.ilike(p), Cita.descripcion.ilike(p)))

    # orden coherente
    if estado_lista == ESTADOS_PENDIENTES:
        consulta = consulta.order_by(Cita.fecha.asc(), Cita.horario.asc())
    else:
        consulta = consulta.order_by(Cita.fecha.desc(), Cita.horario.asc())

    return consulta.all()