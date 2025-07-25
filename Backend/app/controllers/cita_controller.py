from flask import jsonify
from app.models.usuarios import Usuario
from app import db
from app.models.cita import Cita
from datetime import datetime
from sqlalchemy import and_


def crear_cita(data):
    fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    horario = data['horario']
    id_alumno = data['id_alumno']

    # Validar que no haya cruce de horarios (por fecha y horario)
    ya_reservado = Cita.query.filter_by(fecha=fecha, horario=horario).first()
    if ya_reservado:
        return jsonify({'error': 'Ese horario ya está reservado'}), 400

    # Validar que el alumno no tenga otra cita el mismo día
    cita_duplicada = Cita.query.filter_by(id_alumno=id_alumno, fecha=fecha).first()
    if cita_duplicada:
        return jsonify({'error': 'Ya tienes una cita ese día'}), 400

    nueva = Cita(
        id_alumno=id_alumno,
        motivo=data['motivo'],
        descripcion=data['descripcion'],
        area=data['area'],
        fecha=fecha,
        horario=horario,
        id_usuario=data['id_usuario']  # admin o el mismo alumno
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({'mensaje': 'Cita registrada exitosamente'}), 201

def obtener_citas_por_alumno(id_alumno):
    return Cita.query.filter_by(id_alumno=id_alumno).order_by(Cita.fecha.desc()).all()

def obtener_citas_pendientes():
    return Cita.query.filter(Cita.estado.in_(['Solicitado', 'Aprobado', 'Reprogramado'])).order_by(Cita.fecha.asc()).all()

def obtener_citas_culminadas():
    return Cita.query.filter(Cita.estado.in_(['Atendido', 'Ausente'])).order_by(Cita.fecha.desc()).all()

def obtener_cita(id_cita):
    return Cita.query.get(id_cita)

def actualizar_estado_cita(id_cita, nuevo_estado):
    cita = Cita.query.get(id_cita)
    if cita:
        cita.estado = nuevo_estado
        db.session.commit()
        return jsonify({'mensaje': 'Estado actualizado'}), 200
    return jsonify({'error': 'Cita no encontrada'}), 404

from datetime import datetime

def actualizar_citas_ausentes():
    ahora = datetime.now()

    citas = Cita.query.filter(Cita.estado.in_(['Solicitado', 'Aprobado', 'Reprogramado'])).all()
    cambios = 0
    for cita in citas:
        cita_datetime = datetime.combine(cita.fecha, datetime.strptime(cita.horario.split(' - ')[1], "%I:%M%p").time())
        if ahora > cita_datetime:
            cita.estado = 'Ausente'
            cambios += 1

    if cambios:
        db.session.commit()
    return cambios

def reprogramar_cita(id_cita, nueva_fecha, nuevo_horario):
    cita = Cita.query.get(id_cita)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404

    # Validar si ese nuevo horario ya está reservado
    ya_reservado = Cita.query.filter_by(fecha=nueva_fecha, horario=nuevo_horario).first()
    if ya_reservado and ya_reservado.id_cita != id_cita:
        return jsonify({'error': 'Ese nuevo horario ya está reservado'}), 400

    # Validar si el alumno ya tiene otra cita ese mismo día (excepto esta)
    otra_cita = Cita.query.filter(
        Cita.id_alumno == cita.id_alumno,
        Cita.fecha == nueva_fecha,
        Cita.id_cita != id_cita
    ).first()
    if otra_cita:
        return jsonify({'error': 'El alumno ya tiene otra cita ese día'}), 400

    # Actualizar datos
    cita.fecha = nueva_fecha
    cita.horario = nuevo_horario
    cita.estado = 'Reprogramado'
    db.session.commit()

    return jsonify({'mensaje': 'Cita reprogramada correctamente'}), 200

ESTADOS_PENDIENTES  = ['Solicitado', 'Aprobado', 'Reprogramado']
ESTADOS_CULMINADAS  = ['Atendido', 'Ausente']

def filtrar_citas(estado_lista, **filtros):
    """
    estado_lista →  lista de estados que se desean (pendientes o culminadas)
    filtros →       id_alumno, nombre, area, fecha  (cualquiera opcional)
    """
    consulta = Cita.query.join(Cita.alumno).filter(Cita.estado.in_(estado_lista))

    if filtros.get('id_alumno'):
        consulta = consulta.filter(Cita.id_alumno == filtros['id_alumno'])

    if filtros.get('nombre'):
        patron = f"%{filtros['nombre']}%"
        consulta = consulta.filter(Usuario.nombre.ilike(patron))

    if filtros.get('area'):
        consulta = consulta.filter(Cita.area.ilike(filtros['area']))

    if filtros.get('fecha'):
        consulta = consulta.filter(Cita.fecha == filtros['fecha'])

    # orden coherente
    if estado_lista == ESTADOS_PENDIENTES:
        consulta = consulta.order_by(Cita.fecha.asc(), Cita.horario.asc())
    else:
        consulta = consulta.order_by(Cita.fecha.desc(), Cita.horario.asc())

    return consulta.all()