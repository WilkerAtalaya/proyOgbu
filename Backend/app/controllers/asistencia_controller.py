from flask import jsonify
from app import db
from app.models.asistencia import RegistroAsistencia
from app.models.usuarios import Usuario
from sqlalchemy import extract
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
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    registros = RegistroAsistencia.query.filter_by(id_usuario=id_usuario, fecha=fecha)\
        .order_by(RegistroAsistencia.hora_marcado.asc()).all()
    return jsonify([r.to_dict() for r in registros])


def obtener_reporte_admin(fecha_str):
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    registros = RegistroAsistencia.query.filter_by(fecha=fecha).order_by(RegistroAsistencia.hora_marcado.asc()).all()

    resultado = []
    for r in registros:
        usuario = Usuario.query.get(r.id_usuario)
        resultado.append({
            'codigo': usuario.id_usuario if usuario else None,
            'nombre': usuario.nombre if usuario else 'Desconocido',
            'hora': r.hora_marcado.strftime('%H:%M:%S')
        })
    return jsonify(resultado)

def obtener_fechas_asistencia_general():
    registros = RegistroAsistencia.query.with_entities(RegistroAsistencia.fecha).distinct().order_by(RegistroAsistencia.fecha.desc()).all()
    fechas = [r.fecha.isoformat() for r in registros]
    return jsonify(fechas)
