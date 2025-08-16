from flask import Blueprint, request, jsonify
from app.controllers.queja_controller import crear_queja, obtener_quejas_por_usuario, obtener_todas_quejas, actualizar_estado_queja, actualizar_queja_por_alumno
from werkzeug.utils import secure_filename
from datetime import datetime
import os

queja_bp = Blueprint('queja', __name__)
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'quejas'))


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

@queja_bp.route('/quejas/<int:id_queja>', methods=['PUT', 'PATCH'])
def editar_queja_alumno(id_queja):
    """
    Acepta multipart/form-data para permitir cambiar archivo.
    Reglas:
      - Debe enviar id_usuario (por ahora sin auth).
      - Solo edita si estado actual es "Recibido".
      - Campos editables: asunto, motivo, descripcion, prueba (archivo).
      - eliminar_prueba=1 elimina la evidencia sin subir otra.
    """
    id_usuario = request.form.get('id_usuario') or request.args.get('id_usuario')
    if not id_usuario:
        return jsonify({'error': 'id_usuario es obligatorio'}), 400

    # Guardaremos nuevo archivo (si viene)
    new_filename = None
    reemplazo = False

    # Procesar archivo nuevo
    if 'prueba' in request.files and request.files['prueba'].filename:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        up = request.files['prueba']
        fname = secure_filename(up.filename)
        new_filename = f"evidencia_{datetime.now().strftime('%Y%m%d%H%M%S')}_{fname}"
        up.save(os.path.join(UPLOAD_DIR, new_filename))
        reemplazo = True

    eliminar_prueba_flag = request.form.get('eliminar_prueba', '0') == '1'

    # Traer la queja para poder borrar archivo viejo si corresponde
    from app.models.queja import Queja
    q = Queja.query.get(id_queja)
    if not q:
        # si ya subimos archivo, lo borramos para no dejar basura
        if new_filename:
            try: os.remove(os.path.join(UPLOAD_DIR, new_filename))
            except FileNotFoundError: pass
        return jsonify({'error': 'Queja no encontrada'}), 404

    old_file = q.prueba

    # Preparar valores a actualizar
    asunto = request.form.get('asunto', None)
    motivo = request.form.get('motivo', None)
    descripcion = request.form.get('descripcion', None)

    # política de archivo a enviar al controller:
    prueba_value = None
    if reemplazo:
        prueba_value = new_filename
    elif eliminar_prueba_flag:
        prueba_value = ''  # instrucción para borrar

    queja_editada, err = actualizar_queja_por_alumno(
        id_queja=id_queja,
        id_usuario=int(id_usuario),
        asunto=asunto,
        motivo=motivo,
        descripcion=descripcion,
        prueba=prueba_value
    )

    if err == "NOT_FOUND":
        if new_filename:
            try: os.remove(os.path.join(UPLOAD_DIR, new_filename))
            except FileNotFoundError: pass
        return jsonify({'error': 'Queja no encontrada'}), 404
    if err == "FORBIDDEN":
        if new_filename:
            try: os.remove(os.path.join(UPLOAD_DIR, new_filename))
            except FileNotFoundError: pass
        return jsonify({'error': 'No puede editar una queja de otro usuario'}), 403
    if err == "LOCKED":
        if new_filename:
            try: os.remove(os.path.join(UPLOAD_DIR, new_filename))
            except FileNotFoundError: pass
        return jsonify({'error': 'La queja ya no es editable (estado distinto de "Recibido")'}), 409

    # Si reemplazó o eliminó archivo, borrar el anterior del disco
    if (reemplazo or eliminar_prueba_flag) and old_file:
        try: os.remove(os.path.join(UPLOAD_DIR, old_file))
        except FileNotFoundError:
            pass

    return jsonify({
        'mensaje': 'Queja actualizada',
        'codigo': queja_editada.codigo_reporte,
        'estado': queja_editada.estado
    }), 200