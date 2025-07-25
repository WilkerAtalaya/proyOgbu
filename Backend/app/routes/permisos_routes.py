from flask import Blueprint, request
from app.controllers.permisos_controller import (
    crear_salida_vivienda,
    listar_salidas_vivienda,
    actualizar_estado_salida,
    crear_reserva_area_comun,
    listar_reservas_area_comun,
    actualizar_estado_reserva
)

permisos_bp = Blueprint('permisos', __name__, url_prefix='/api/permisos')

# RUTAS: Salida Vivienda

@permisos_bp.route('/salida', methods=['POST'])
def registrar_salida():
    return crear_salida_vivienda()

@permisos_bp.route('/salida/usuario/<int:id_usuario>', methods=['GET'])
def obtener_salidas_usuario(id_usuario):
    return listar_salidas_vivienda(id_usuario)

@permisos_bp.route('/salida/admin', methods=['GET'])
def obtener_salidas_admin():
    return listar_salidas_vivienda()

@permisos_bp.route('/salida/<int:id_salida>/estado', methods=['PUT'])
def cambiar_estado_salida(id_salida):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    return actualizar_estado_salida(id_salida, nuevo_estado)


# RUTAS: Área Común

@permisos_bp.route('/area-comun', methods=['POST'])
def registrar_reserva():
    return crear_reserva_area_comun()

@permisos_bp.route('/area-comun/usuario/<int:id_usuario>', methods=['GET'])
def obtener_reservas_usuario(id_usuario):
    return listar_reservas_area_comun(id_usuario)

@permisos_bp.route('/area-comun/admin', methods=['GET'])
def obtener_reservas_admin():
    return listar_reservas_area_comun()

@permisos_bp.route('/area-comun/<int:id_reserva>/estado', methods=['PUT'])
def cambiar_estado_reserva(id_reserva):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    return actualizar_estado_reserva(id_reserva, nuevo_estado)