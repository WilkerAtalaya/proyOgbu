from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.usuarios import Usuario
from app.controllers.usuario_controllers import obtener_cumpleaños_hoy
from app import db

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{
        "id": u.id_usuario,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol
    } for u in usuarios])

@usuarios_bp.route('/cumpleaños', methods=['GET'])
def cumpleaños_hoy():
    usuarios = obtener_cumpleaños_hoy()
    resultado = [{
        'id': u.id_usuario,
        'nombre': u.nombre,
        'fecha_cumpleaños': u.fecha_cumpleaños.isoformat()
    } for u in usuarios]
    return jsonify(resultado)

@usuarios_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data.get('correo')
    contraseña = data.get('contraseña')

    usuario = Usuario.query.filter_by(correo=correo).first()
    if not usuario or not check_password_hash(usuario.contraseña, contraseña):
        return jsonify({'mensaje': 'Credenciales inválidas'}), 401

    return jsonify({
        "id": usuario.id_usuario,
        "nombre": usuario.nombre,
        "rol": usuario.rol
    }), 200


# === NUEVO: Cambiar contraseña desde el login ===
@usuarios_bp.route('/cambiar-contraseña', methods=['POST'])
def cambiar_contraseña():
    """
    Body esperado (JSON):
    {
        "correo": "user@dominio.com",
        "contraseña_actual": "Actual123",
        "nueva_contraseña": "Nueva123!"
    }
    """
    data = request.get_json() or {}
    correo = data.get('correo')
    actual = data.get('contraseña_actual')
    nueva = data.get('nueva_contraseña')

    if not correo or not actual or not nueva:
        return jsonify({"mensaje": "correo, contraseña_actual y nueva_contraseña son obligatorios."}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()
    if not usuario or not check_password_hash(usuario.contraseña, actual):
        return jsonify({"mensaje": "Usuario no encontrado o contraseña actual incorrecta."}), 401

    # Validaciones mínimas (ajuste según su política)
    if len(nueva) < 8:
        return jsonify({"mensaje": "La nueva contraseña debe tener al menos 8 caracteres."}), 400
    if nueva == actual:
        return jsonify({"mensaje": "La nueva contraseña no puede ser igual a la actual."}), 400

    usuario.contraseña = generate_password_hash(nueva, method='pbkdf2:sha256')
    db.session.commit()
    return jsonify({"mensaje": "Contraseña actualizada correctamente."}), 200