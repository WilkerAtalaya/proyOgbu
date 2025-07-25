from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash
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



    
    