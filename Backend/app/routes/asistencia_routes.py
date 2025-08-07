from flask import Blueprint, request
from app.controllers.asistencia_controller import (
    registrar_asistencia,
    obtener_fechas_asistencia,
    obtener_detalle_por_fecha,
    obtener_reporte_admin_filtrado,     
    obtener_fechas_asistencia_general,
    obtener_reporte_alumno_por_fecha    
)

asistencia_bp = Blueprint('asistencia', __name__)

@asistencia_bp.route('/asistencia', methods=['POST'])
def marcar_asistencia():
    return registrar_asistencia(request.get_json())

@asistencia_bp.route('/asistencia/fechas/<int:id_usuario>', methods=['GET'])
def ver_fechas(id_usuario):
    return obtener_fechas_asistencia(id_usuario)

@asistencia_bp.route('/asistencia/detalle/<int:id_usuario>/<fecha>', methods=['GET'])
def ver_detalle_dia(id_usuario, fecha):
    return obtener_detalle_por_fecha(id_usuario, fecha)

@asistencia_bp.route('/asistencia/admin/reporte', methods=['GET'])
def ver_reporte_admin_filtrado():
    return obtener_reporte_admin_filtrado()

@asistencia_bp.route('/asistencia/alumno/<int:id_usuario>/reporte', methods=['GET'])
def ver_reporte_alumno(id_usuario):
    return obtener_reporte_alumno_por_fecha(id_usuario)

@asistencia_bp.route('/asistencia/admin/fechas', methods=['GET'])
def ver_fechas_asistencia_general():
    return obtener_fechas_asistencia_general()
