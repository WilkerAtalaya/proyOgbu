from flask import request, jsonify
from app.models.permisos import SalidaVivienda, ReservaAreaComun, db
from datetime import datetime

# ----- SALIDA DE VIVIENDA -----

def crear_salida_vivienda():
    data = request.get_json()
    id_usuario = data.get('id_usuario')
    fecha_salida = datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date()
    fecha_regreso = datetime.strptime(data['fecha_regreso'], '%Y-%m-%d').date()
    motivo = data.get('motivo', None)

    dias_diferencia = (fecha_regreso - fecha_salida).days
    if dias_diferencia > 10 and not motivo:
        return jsonify({'error': 'Debe ingresar un motivo si su salida es mayor a 10 días.'}), 400

    nueva_salida = SalidaVivienda(
        id_usuario=id_usuario,
        fecha_salida=fecha_salida,
        fecha_regreso=fecha_regreso,
        motivo=motivo
    )

    db.session.add(nueva_salida)
    db.session.commit()

    return jsonify({'message': 'Solicitud registrada correctamente'}), 201


def listar_salidas_vivienda(id_usuario=None):
    if id_usuario:
        salidas = SalidaVivienda.query.filter_by(id_usuario=id_usuario).all()
    else:
        salidas = SalidaVivienda.query.all()

    return jsonify([s.to_dict() for s in salidas])


def actualizar_estado_salida(id_salida, nuevo_estado):
    salida = SalidaVivienda.query.get(id_salida)
    if not salida:
        return jsonify({'error': 'Salida no encontrada'}), 404

    salida.estado = nuevo_estado
    db.session.commit()
    return jsonify({'message': 'Estado actualizado correctamente'})


# ----- ÁREA COMÚN -----

def crear_reserva_area_comun():
    data = request.get_json()
    id_usuario = data.get('id_usuario')
    lugar = data['lugar']
    fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    horario = data['horario']

    # 1. Otra persona ya reservó ese lugar-fecha-horario
    reserva_existente = ReservaAreaComun.query.filter(
        ReservaAreaComun.lugar == lugar,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.horario == horario,
        ReservaAreaComun.estado != 'Denegado'
    ).first()

    if reserva_existente:
        return jsonify({'error': 'Ese lugar ya está reservado para esa fecha y horario.'}), 409

    # 2. Mismo usuario ya reservó algo ese día y en ese mismo horario
    conflicto_usuario = ReservaAreaComun.query.filter(
        ReservaAreaComun.id_usuario == id_usuario,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.horario == horario,
        ReservaAreaComun.estado != 'Denegado'
    ).first()

    if conflicto_usuario:
        return jsonify({'error': 'Usted ya tiene una reserva en ese horario para esa fecha.'}), 409

    # 3. Mismo usuario ya reservó ese lugar en otro horario ese mismo día
    repetido = ReservaAreaComun.query.filter(
        ReservaAreaComun.id_usuario == id_usuario,
        ReservaAreaComun.lugar == lugar,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.estado != 'Denegado'
    ).first()

    if repetido:
        return jsonify({'error': 'Ya tiene una reserva para ese lugar en esa fecha.'}), 409

    nueva_reserva = ReservaAreaComun(
        id_usuario=id_usuario,
        lugar=lugar,
        fecha=fecha,
        horario=horario
    )

    db.session.add(nueva_reserva)
    db.session.commit()

    return jsonify({'message': 'Reserva registrada correctamente'}), 201




def listar_reservas_area_comun(id_usuario=None):
    if id_usuario:
        reservas = ReservaAreaComun.query.filter_by(id_usuario=id_usuario).all()
    else:
        reservas = ReservaAreaComun.query.all()

    return jsonify([r.to_dict() for r in reservas])


def actualizar_estado_reserva(id_reserva, nuevo_estado):
    reserva = ReservaAreaComun.query.get(id_reserva)
    if not reserva:
        return jsonify({'error': 'Reserva no encontrada'}), 404

    reserva.estado = nuevo_estado
    db.session.commit()
    return jsonify({'message': 'Estado actualizado correctamente'})
