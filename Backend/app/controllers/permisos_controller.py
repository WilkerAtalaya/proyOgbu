import uuid
from flask import request, jsonify, url_for, redirect
from sqlalchemy import desc
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.models.permisos import SalidaVivienda, ReservaAreaComun, db
from app.models.usuarios import Usuario
from app.files.service import save_upload, file_url

LIMA_TZ = ZoneInfo('America/Lima')
BUCKET_JUST = 'justificacion'  # bucket único para justificantes

def _to_lima_iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LIMA_TZ).isoformat(timespec='seconds')

# ========== SALIDA DE VIVIENDA ==========

def crear_salida_vivienda():
    if request.content_type and 'multipart/form-data' in request.content_type:
        form = request.form
        file = request.files.get('archivo')  # archivo único (opcional)
        id_usuario = int(form['id_usuario'])
        fecha_salida = datetime.strptime(form['fecha_salida'], '%Y-%m-%d').date()
        fecha_regreso = datetime.strptime(form['fecha_regreso'], '%Y-%m-%d').date()
        motivo = form.get('motivo')
    else:
        data = request.get_json(force=True, silent=True) or {}
        file = None
        id_usuario = int(data['id_usuario'])
        fecha_salida = datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date()
        fecha_regreso = datetime.strptime(data['fecha_regreso'], '%Y-%m-%d').date()
        motivo = data.get('motivo')

    if (fecha_regreso - fecha_salida).days > 10 and not motivo:
        return jsonify({'error': 'Debe ingresar un motivo si su salida es mayor a 10 días.'}), 400

    salida = SalidaVivienda(
        id_usuario=id_usuario,
        fecha_salida=fecha_salida,
        fecha_regreso=fecha_regreso,
        motivo=motivo
    )

    # Guardar archivo si vino
    if file and file.filename:
        meta, err = save_upload(file, BUCKET_JUST, modes=('images','docs'))
        if err:
            return jsonify({'error': f'Archivo no permitido ({err})'}), 400
        salida.archivo_justificacion = meta['stored_name']

    db.session.add(salida)
    db.session.commit()

    return jsonify({
        'message': 'Solicitud registrada correctamente',
        'id_solicitud': salida.id,
        'archivo': _to_archivo_obj(salida.archivo_justificacion)
    }), 201

def _to_archivo_obj(stored_name: str | None):
    if not stored_name:
        return None
    return {
        "bucket": BUCKET_JUST,
        "stored_name": stored_name,
        "original_name": stored_name.split('_', 1)[-1] if '_' in stored_name else stored_name,
        "mime": None,
        "size": None,
        "url": file_url(BUCKET_JUST, stored_name, external=True)
    }

def _serialize_salida(s: SalidaVivienda):
    return {
        'id': s.id,
        'id_usuario': s.id_usuario,
        'nombre_usuario': s.usuario.nombre if s.usuario else None,
        'fecha_salida': s.fecha_salida.strftime('%Y-%m-%d'),
        'fecha_regreso': s.fecha_regreso.strftime('%Y-%m-%d'),
        'motivo': s.motivo,
        'estado': s.estado,
        'Fecha_solicitada': _to_lima_iso(s.Fecha_solicitada),
        'archivo': _to_archivo_obj(s.archivo_justificacion),
    }

def listar_salidas_vivienda(id_usuario=None):
    q = SalidaVivienda.query.join(Usuario, SalidaVivienda.id_usuario == Usuario.id_usuario)
    if id_usuario:
        q = q.filter(SalidaVivienda.id_usuario == id_usuario)
    else:
        estado = request.args.get('estado')
        nombre = request.args.get('nombre')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        if estado:
            q = q.filter(SalidaVivienda.estado == estado)
        if nombre:
            q = q.filter(Usuario.nombre.ilike(f"%{nombre.strip()}%"))
        if fecha_desde:
            try:
                fd = datetime.strptime(fecha_desde, '%Y-%m-%d')
                q = q.filter(SalidaVivienda.Fecha_solicitada >= fd)
            except ValueError:
                return jsonify({'error': 'fecha_desde inválida. Use YYYY-MM-DD'}), 400
        if fecha_hasta:
            try:
                fh = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                q = q.filter(SalidaVivienda.Fecha_solicitada <= fh)
            except ValueError:
                return jsonify({'error': 'fecha_hasta inválida. Use YYYY-MM-DD'}), 400

    salidas = q.order_by(desc(SalidaVivienda.Fecha_solicitada)).all()
    return jsonify([_serialize_salida(s) for s in salidas])

def actualizar_estado_salida(id_salida, nuevo_estado):
    s = SalidaVivienda.query.get(id_salida)
    if not s:
        return jsonify({'error': 'Salida no encontrada'}), 404
    s.estado = nuevo_estado
    db.session.commit()
    return jsonify({'message': 'Estado actualizado correctamente'})

# Mantén este endpoint si tu front antiguo lo usa: redirige al nuevo /files/...
def descargar_justificacion_file(filename):
    return redirect(file_url(BUCKET_JUST, filename, external=True))

# ========== ÁREA COMÚN ==========

def crear_reserva_area_comun():
    if request.content_type and 'multipart/form-data' in request.content_type:
        form = request.form
        id_usuario = int(form['id_usuario'])
        lugar = form['lugar']
        fecha = datetime.strptime(form['fecha'], '%Y-%m-%d').date()
        horario = form['horario']
        motivo = form.get('motivo')
    else:
        data = request.get_json(force=True, silent=True) or {}
        id_usuario = int(data['id_usuario'])
        lugar = data['lugar']
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        horario = data['horario']
        motivo = data.get('motivo')

    # Reglas de conflicto
    if ReservaAreaComun.query.filter(
        ReservaAreaComun.lugar == lugar,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.horario == horario,
        ReservaAreaComun.estado != 'Denegado'
    ).first():
        return jsonify({'error': 'Ese lugar ya está reservado para esa fecha y horario.'}), 409

    if ReservaAreaComun.query.filter(
        ReservaAreaComun.id_usuario == id_usuario,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.horario == horario,
        ReservaAreaComun.estado != 'Denegado'
    ).first():
        return jsonify({'error': 'Usted ya tiene una reserva en ese horario para esa fecha.'}), 409

    if ReservaAreaComun.query.filter(
        ReservaAreaComun.id_usuario == id_usuario,
        ReservaAreaComun.lugar == lugar,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.estado != 'Denegado'
    ).first():
        return jsonify({'error': 'Ya tiene una reserva para ese lugar en esa fecha.'}), 409

    r = ReservaAreaComun(
        id_usuario=id_usuario, lugar=lugar, fecha=fecha, horario=horario, motivo=motivo
    )
    db.session.add(r)
    db.session.commit()

    return jsonify({'message': 'Reserva registrada correctamente', 'id_reserva': r.id}), 201

def _serialize_reserva(r: ReservaAreaComun):
    return {
        'id': r.id,
        'id_usuario': r.id_usuario,
        'nombre_usuario': r.usuario.nombre if r.usuario else None,
        'lugar': r.lugar,
        'fecha': r.fecha.strftime('%Y-%m-%d'),
        'horario': r.horario,
        'estado': r.estado,
        'motivo': r.motivo,
        'Fecha_solicitada': _to_lima_iso(r.Fecha_solicitada),
    }

def listar_reservas_area_comun(id_usuario=None):
    q = ReservaAreaComun.query.join(Usuario, ReservaAreaComun.id_usuario == Usuario.id_usuario)
    if id_usuario:
        q = q.filter(ReservaAreaComun.id_usuario == id_usuario)
    else:
        estado = request.args.get('estado')
        nombre = request.args.get('nombre')
        lugar = request.args.get('lugar')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        if estado:
            q = q.filter(ReservaAreaComun.estado == estado)
        if nombre:
            q = q.filter(Usuario.nombre.ilike(f"%{nombre.strip()}%"))
        if lugar:
            q = q.filter(ReservaAreaComun.lugar.ilike(f"%{lugar.strip()}%"))
        if fecha_desde:
            try:
                fd = datetime.strptime(fecha_desde, '%Y-%m-%d')
                q = q.filter(ReservaAreaComun.Fecha_solicitada >= fd)
            except ValueError:
                return jsonify({'error': 'fecha_desde inválida. Use YYYY-MM-DD'}), 400
        if fecha_hasta:
            try:
                fh = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                q = q.filter(ReservaAreaComun.Fecha_solicitada <= fh)
            except ValueError:
                return jsonify({'error': 'fecha_hasta inválida. Use YYYY-MM-DD'}), 400

    reservas = q.order_by(desc(ReservaAreaComun.Fecha_solicitada)).all()
    return jsonify([_serialize_reserva(r) for r in reservas])

def actualizar_estado_reserva(id_reserva, nuevo_estado):
    r = ReservaAreaComun.query.get(id_reserva)
    if not r:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    r.estado = nuevo_estado
    db.session.commit()
    return jsonify({'message': 'Estado actualizado correctamente'})
