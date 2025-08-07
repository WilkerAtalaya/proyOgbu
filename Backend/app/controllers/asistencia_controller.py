from flask import jsonify, request
from app import db
from app.models.asistencia import RegistroAsistencia
from app.models.usuarios import Usuario
from datetime import datetime, date


def registrar_asistencia(data):
    id_usuario = data.get('id_usuario')
    if not id_usuario:
        return jsonify({'error': 'ID de usuario faltante'}), 400

    alumno = Usuario.query.get(id_usuario)
    if not alumno or alumno.rol != 'alumno':
        return jsonify({'error': 'Alumno no encontrado'}), 404

    nueva = RegistroAsistencia(id_usuario=id_usuario)
    db.session.add(nueva)
    db.session.commit()

    return jsonify({'mensaje': 'Asistencia registrada', 'hora': nueva.hora_marcado.isoformat()}), 201


def obtener_fechas_asistencia(id_usuario):
    registros = RegistroAsistencia.query.filter_by(id_usuario=id_usuario).all()
    fechas_unicas = sorted(set(r.fecha for r in registros), reverse=True)
    return jsonify([f.isoformat() for f in fechas_unicas])


def obtener_detalle_por_fecha(id_usuario, fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}), 400

    registros = (RegistroAsistencia.query
                 .filter_by(id_usuario=id_usuario, fecha=fecha)
                 .order_by(RegistroAsistencia.hora_marcado.asc())
                 .all())
    return jsonify([r.to_dict() for r in registros])


def obtener_fechas_asistencia_general():
    registros = (RegistroAsistencia.query
                 .with_entities(RegistroAsistencia.fecha)
                 .distinct()
                 .order_by(RegistroAsistencia.fecha.desc())
                 .all())
    fechas = [r.fecha.isoformat() for r in registros]
    return jsonify(fechas)


def obtener_reporte_admin_filtrado():
    
    fecha_str = request.args.get('fecha', '').strip()
    id_param = request.args.get('id', '').strip()
    nombre_param = request.args.get('nombre', '').strip()
    limit_param = request.args.get('limit', '').strip()

    try:
        limit = int(limit_param) if limit_param else 200
        limit = max(1, min(limit, 2000))  # no más de 2000
    except ValueError:
        return jsonify({'error': 'El parámetro "limit" debe ser numérico.'}), 400

    q = (db.session.query(RegistroAsistencia, Usuario)
         .join(Usuario, RegistroAsistencia.id_usuario == Usuario.id_usuario)
         .filter(Usuario.rol == 'alumno'))

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD).'}), 400
        q = q.filter(RegistroAsistencia.fecha == fecha)

    if id_param:
        try:
            id_int = int(id_param)
        except ValueError:
            return jsonify({'error': 'El parámetro "id" debe ser numérico.'}), 400
        q = q.filter(RegistroAsistencia.id_usuario == id_int)

    if nombre_param:
        q = q.filter(Usuario.nombre.ilike(f'%{nombre_param}%'))

    q = q.order_by(RegistroAsistencia.fecha.desc(),
                   RegistroAsistencia.hora_marcado.asc())

    registros = q.limit(limit).all()

    resultado = [{
        'codigo': u.id_usuario,
        'nombre': u.nombre,
        'fecha': r.fecha.isoformat(),
        'hora': r.hora_marcado.strftime('%H:%M:%S')
    } for r, u in registros]

    return jsonify(resultado)



def obtener_reporte_alumno_por_fecha(id_usuario):
    fecha_str = request.args.get('fecha', '').strip()
    if not fecha_str:
        return jsonify({'error': 'El parámetro "fecha" es obligatorio (YYYY-MM-DD).'}), 400

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD).'}), 400

    registros = (RegistroAsistencia.query
                 .filter_by(id_usuario=id_usuario, fecha=fecha)
                 .order_by(RegistroAsistencia.hora_marcado.asc())
                 .all())

    return jsonify([r.to_dict() for r in registros])
