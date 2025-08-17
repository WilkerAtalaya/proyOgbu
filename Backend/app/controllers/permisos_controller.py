# app/controllers/permisos_controller.py
import os, uuid
from flask import request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import desc
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

LIMA_TZ = ZoneInfo('America/Lima')

def _to_lima_iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LIMA_TZ).isoformat(timespec='seconds')

from app.models.permisos import (
    SalidaVivienda, ReservaAreaComun, db
)
from app.models.usuarios import Usuario

# --- Config de uploads (solo para Salida de vivienda) ---
ALLOWED_EXT = {'pdf','doc','docx','xls','xlsx','ppt','pptx','txt','jpg','jpeg','png','gif','webp'}

def _ext_ok(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def _justificacion_dir():
    # raíz del proyecto: controllers/../../
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    path = os.path.join(base, 'uploads', 'justificacion')
    os.makedirs(path, exist_ok=True)
    return path


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
        if not _ext_ok(file.filename):
            return jsonify({'error': 'Extensión no permitida'}), 400
        ext = file.filename.rsplit('.', 1)[1].lower()
        fname = secure_filename(f"{uuid.uuid4().hex}.{ext}")
        file.save(os.path.join(_justificacion_dir(), fname))
        salida.archivo_justificacion = fname

    db.session.add(salida)
    db.session.commit()

    return jsonify({'message': 'Solicitud registrada correctamente', 'id_solicitud': salida.id}), 201


def _serialize_salida(s):
    archivo_url = None
    if s.archivo_justificacion:
        archivo_url = url_for('permisos.descargar_justificacion', filename=s.archivo_justificacion, _external=True)

    return {
        'id': s.id,
        'id_usuario': s.id_usuario,
        'nombre_usuario': s.usuario.nombre if s.usuario else None,
        'fecha_salida': s.fecha_salida.strftime('%Y-%m-%d'),
        'fecha_regreso': s.fecha_regreso.strftime('%Y-%m-%d'),
        'motivo': s.motivo,
        'estado': s.estado,
        'Fecha_solicitada': _to_lima_iso(s.Fecha_solicitada),
        'archivo_justificacion': s.archivo_justificacion,
        'archivo_url': archivo_url
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
    salida = SalidaVivienda.query.get(id_salida)
    if not salida:
        return jsonify({'error': 'Salida no encontrada'}), 404
    salida.estado = nuevo_estado
    db.session.commit()
    return jsonify({'message': 'Estado actualizado correctamente'})


def descargar_justificacion_file(filename):
    return send_from_directory(_justificacion_dir(), filename, as_attachment=False)


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
    reserva_existente = ReservaAreaComun.query.filter(
        ReservaAreaComun.lugar == lugar,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.horario == horario,
        ReservaAreaComun.estado != 'Denegado'
    ).first()
    if reserva_existente:
        return jsonify({'error': 'Ese lugar ya está reservado para esa fecha y horario.'}), 409

    conflicto_usuario = ReservaAreaComun.query.filter(
        ReservaAreaComun.id_usuario == id_usuario,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.horario == horario,
        ReservaAreaComun.estado != 'Denegado'
    ).first()
    if conflicto_usuario:
        return jsonify({'error': 'Usted ya tiene una reserva en ese horario para esa fecha.'}), 409

    repetido = ReservaAreaComun.query.filter(
        ReservaAreaComun.id_usuario == id_usuario,
        ReservaAreaComun.lugar == lugar,
        ReservaAreaComun.fecha == fecha,
        ReservaAreaComun.estado != 'Denegado'
    ).first()
    if repetido:
        return jsonify({'error': 'Ya tiene una reserva para ese lugar en esa fecha.'}), 409

    reserva = ReservaAreaComun(
        id_usuario=id_usuario,
        lugar=lugar,
        fecha=fecha,
        horario=horario,
        motivo=motivo
    )
    db.session.add(reserva)
    db.session.commit()

    return jsonify({'message': 'Reserva registrada correctamente', 'id_reserva': reserva.id}), 201

def _serialize_reserva(r):
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
    reserva = ReservaAreaComun.query.get(id_reserva)
    if not reserva:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    reserva.estado = nuevo_estado
    db.session.commit()
    return jsonify({'message': 'Estado actualizado correctamente'})
