from flask import Blueprint, request, jsonify
from app import db
from app.models.usuarios import Usuario, ROLES_PERMITIDOS, ESTADOS_PERMITIDOS, RESIDENCIAS_PERMITIDAS
from app.controllers.administrar_usuario_controller import (
    crear_usuario_admin,
    listar_usuarios_admin,
    obtener_usuario_admin,
    actualizar_usuario_admin,
    cambiar_estado_usuario_admin,
)

administrar_usuario_bp = Blueprint("administrar_usuarios", __name__, url_prefix="/admin/usuarios")


# ====== Helper: verificar que el solicitante es admin ======
def _es_admin():
    """
    Ajusta este helper a tu esquema real de auth (JWT/sesión).
    Por simplicidad, se toma un header X-ROL: admin
    """
    rol_header = (request.headers.get("X-ROL") or "").strip().lower()
    return rol_header == "admin"


def _req_admin_or_401():
    if not _es_admin():
        return jsonify({"mensaje": "No autorizado. Se requiere rol admin."}), 401
    return None


# ====== Crear usuario ======
@administrar_usuario_bp.route("", methods=["POST"])
def crear_usuario():
    noauth = _req_admin_or_401()
    if noauth:
        return noauth

    payload = request.get_json() or {}
    u, err = crear_usuario_admin(payload)
    if err:
        return jsonify({"mensaje": err}), 400

    return jsonify({
        "id": u.id_usuario,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol,
        "fecha_cumpleaños": u.fecha_cumpleaños.isoformat() if u.fecha_cumpleaños else None,
        "estado": u.estado,
        "residencia": u.residencia,
        "pabellon": u.pabellon,
        "habitacion": u.habitacion,
        "fecha_registro": u.fecha_registro.isoformat() if u.fecha_registro else None
    }), 201


# ====== Listar con filtros ======
@administrar_usuario_bp.route("", methods=["GET"])
def listar_usuarios():
    noauth = _req_admin_or_401()
    if noauth:
        return noauth

    nombre = request.args.get("nombre")
    rol = request.args.get("rol")
    estado = request.args.get("estado")
    residencia = request.args.get("residencia")
    f_desde = request.args.get("fecha_registro_desde")
    f_hasta = request.args.get("fecha_registro_hasta")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    pag, err = listar_usuarios_admin(
        nombre=nombre,
        rol=rol,
        estado=estado,
        residencia=residencia,
        fecha_registro_desde=f_desde,
        fecha_registro_hasta=f_hasta,
        page=page,
        per_page=per_page,
    )
    if err:
        return jsonify({"mensaje": err}), 400

    data = [{
        "id": u.id_usuario,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol,
        "fecha_cumpleaños": u.fecha_cumpleaños.isoformat() if u.fecha_cumpleaños else None,
        "estado": u.estado,
        "residencia": u.residencia,
        "pabellon": u.pabellon,
        "habitacion": u.habitacion,
        "fecha_registro": u.fecha_registro.isoformat() if u.fecha_registro else None
    } for u in pag.items]

    return jsonify({
        "items": data,
        "page": pag.page,
        "per_page": pag.per_page,
        "total": pag.total,
        "pages": pag.pages
    }), 200


# ====== Obtener uno ======
@administrar_usuario_bp.route("/<int:id_usuario>", methods=["GET"])
def obtener_usuario(id_usuario):
    noauth = _req_admin_or_401()
    if noauth:
        return noauth

    u = obtener_usuario_admin(id_usuario)
    if not u:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    return jsonify({
        "id": u.id_usuario,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol,
        "fecha_cumpleaños": u.fecha_cumpleaños.isoformat() if u.fecha_cumpleaños else None,
        "estado": u.estado,
        "residencia": u.residencia,
        "pabellon": u.pabellon,
        "habitacion": u.habitacion,
        "fecha_registro": u.fecha_registro.isoformat() if u.fecha_registro else None
    }), 200


# ====== Actualizar (PUT/PATCH) ======
@administrar_usuario_bp.route("/<int:id_usuario>", methods=["PUT", "PATCH"])
def actualizar_usuario(id_usuario):
    noauth = _req_admin_or_401()
    if noauth:
        return noauth

    payload = request.get_json() or {}
    u, err = actualizar_usuario_admin(id_usuario, payload)
    if err:
        return jsonify({"mensaje": err}), 400

    return jsonify({
        "id": u.id_usuario,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol,
        "fecha_cumpleaños": u.fecha_cumpleaños.isoformat() if u.fecha_cumpleaños else None,
        "estado": u.estado,
        "residencia": u.residencia,
        "pabellon": u.pabellon,
        "habitacion": u.habitacion,
        "fecha_registro": u.fecha_registro.isoformat() if u.fecha_registro else None
    }), 200


# ====== Cambiar estado rápido ======
@administrar_usuario_bp.route("/<int:id_usuario>/estado", methods=["PATCH"])
def cambiar_estado(id_usuario):
    noauth = _req_admin_or_401()
    if noauth:
        return noauth

    data = request.get_json() or {}
    nuevo = (data.get("estado") or "").strip()
    u, err = cambiar_estado_usuario_admin(id_usuario, nuevo)
    if err:
        return jsonify({"mensaje": err}), 400

    return jsonify({
        "id": u.id_usuario,
        "estado": u.estado
    }), 200
