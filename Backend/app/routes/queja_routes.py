from flask import Blueprint, request, jsonify
from app.controllers.queja_controller import crear_queja, obtener_quejas_por_usuario, obtener_todas_quejas, actualizar_estado_queja
from werkzeug.utils import secure_filename
from datetime import datetime
import os

queja_bp = Blueprint('queja', __name__)

@queja_bp.route('/quejas', methods=['POST'])
def registrar_queja():
    asunto = request.form.get("asunto")
    motivo = request.form.get("motivo")
    descripcion = request.form.get("descripcion")
    id_usuario = request.form.get("id_usuario")

    archivo = request.files.get("prueba")
    nombre_archivo = None

    if archivo:
        if not os.path.exists("uploads/quejas"):
            os.makedirs("uploads/quejas", exist_ok=True)
        filename = secure_filename(archivo.filename)
        nombre_archivo = f"evidencia_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        ruta_destino = os.path.join("uploads/quejas", nombre_archivo)
        archivo.save(ruta_destino)

    data = {
        "asunto": asunto,
        "motivo": motivo,
        "descripcion": descripcion,
        "prueba": nombre_archivo,
        "id_usuario": id_usuario
    }

    nueva = crear_queja(data)
    return jsonify({
        "mensaje": "Queja registrada",
        "codigo_reporte": nueva.codigo_reporte
    }), 201

@queja_bp.route('/quejas/usuario/<int:id_usuario>', methods=['GET'])
def listar_quejas_usuario(id_usuario):
    quejas = obtener_quejas_por_usuario(id_usuario)
    return jsonify([{
        'codigo': q.codigo_reporte,
        'asunto': q.asunto,
        'motivo': q.motivo,
        'descripcion': q.descripcion,
        'fecha': q.fecha.strftime('%d/%m/%Y'),
        'estado': q.estado,
        'prueba': q.prueba
    } for q in quejas])

@queja_bp.route('/quejas', methods=['GET'])
def listar_todas_quejas():
    estado = request.args.get('estado', type=str)
    nombre = request.args.get('nombre', type=str)   
    motivo = request.args.get('motivo', type=str)

    fecha_desde_str = request.args.get('fecha_desde', type=str)  
    fecha_hasta_str = request.args.get('fecha_hasta', type=str)

    fecha_desde = None
    fecha_hasta = None

  
    if fecha_desde_str:
        try:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d')
        except ValueError:
            pass
    if fecha_hasta_str:
        try:
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d')
        except ValueError:
            pass

    filtros = {
        'estado': estado if estado else None,
        'nombre': nombre if nombre else None,
        'motivo': motivo if motivo else None,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    }

    quejas = obtener_todas_quejas(filtros)

    return jsonify([{
        'id': q.id_queja,
        'codigo': q.codigo_reporte,
        'asunto': q.asunto,
        'motivo': q.motivo,
        'descripcion': q.descripcion,
        'fecha': q.fecha.strftime('%d/%m/%Y'),
        'estado': q.estado,
        'prueba': q.prueba
    } for q in quejas])

@queja_bp.route('/quejas/<int:id_queja>/estado', methods=['PUT'])
def cambiar_estado_queja(id_queja):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    queja_actualizada = actualizar_estado_queja(id_queja, nuevo_estado)
    if queja_actualizada:
        return jsonify({'mensaje': 'Estado actualizado'}), 200
    return jsonify({'error': 'Queja no encontrada'}), 404
