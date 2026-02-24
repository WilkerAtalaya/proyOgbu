from flask import Blueprint, request, jsonify
from typing import Optional, Tuple
from datetime import datetime

from werkzeug.security import generate_password_hash

from app import db
from app.models.usuarios import Usuario
from app.models.rol import Rol
from sqlalchemy import func

ESTADOS_PERMITIDOS = {"activo", "inactivo"}
RESIDENCIAS_PERMITIDAS = {"Ciudad", "Tello"}

# OJO: El url_prefix "/admin" se coloca al registrar el blueprint:
# app.register_blueprint(administrar_bp, url_prefix="/admin")
administrar_bp = Blueprint("administrar", __name__)

# ===========================
# Helpers internos
# ===========================

def _parse_fecha(d: Optional[str]) -> Optional[datetime.date]:
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def _get_rol_by_slug(slug: Optional[str]) -> Optional[Rol]:
    if not slug:
        return None
    return Rol.query.filter(func.lower(Rol.slug) == slug.strip().lower()).first()


def _usuario_to_dict(u: Usuario) -> dict:
    # No exponemos contraseña
    return {
        "id_usuario": getattr(u, "id_usuario", None) or getattr(u, "id", None),
        "nombre": u.nombre,
        "correo": u.correo,
        # si tu modelo NO tiene "rol" directo, quedará None (y está bien)
        "rol": getattr(u, "rol", None),
        "rol_id": getattr(u, "rol_id", None),
        "estado": getattr(u, "estado", None),
        "residencia": getattr(u, "residencia", None),
        "pabellon": getattr(u, "pabellon", None),
        "habitacion": getattr(u, "habitacion", None),
        "fecha_cumpleanos": str(getattr(u, "fecha_cumpleaños", None)) if getattr(u, "fecha_cumpleaños", None) else None,
        "fecha_registro": str(getattr(u, "fecha_registro", None)) if getattr(u, "fecha_registro", None) else None,
    }


def _get_payload_password(payload: dict) -> str:
    """
    Acepta ambas keys por compatibilidad:
    - "contrasena" (sin ñ)
    - "contraseña" (con ñ)
    """
    return (payload.get("contrasena") or payload.get("contraseña") or "").strip()


def _get_payload_birthday(payload: dict) -> Optional[datetime.date]:
    """
    Acepta ambas keys por compatibilidad:
    - "fecha_cumpleanos"
    - "fecha_cumpleaños"
    """
    raw = payload.get("fecha_cumpleanos")
    if raw is None:
        raw = payload.get("fecha_cumpleaños")
    return _parse_fecha(raw)


# ===========================
# Casos de uso (CRUD)
# ===========================

def crear_usuario_admin(payload: dict) -> Tuple[Optional[Usuario], Optional[str]]:
    nombre = (payload.get("nombre") or "").strip()
    correo = (payload.get("correo") or "").strip()
    contrasena = _get_payload_password(payload)
    rol_slug = (payload.get("rol") or "").strip()

    if not nombre:
        return None, "nombre es requerido"
    if not correo:
        return None, "correo es requerido"
    if not contrasena:
        return None, "contrasena es requerida"
    if not rol_slug:
        return None, "rol (slug) es requerido"

    rol = _get_rol_by_slug(rol_slug)
    if not rol:
        return None, "rol inválido"

    estado = (payload.get("estado") or "").strip() or None
    if estado and estado not in ESTADOS_PERMITIDOS:
        return None, "estado inválido"

    residencia = (payload.get("residencia") or "").strip() or None
    if residencia and residencia not in RESIDENCIAS_PERMITIDAS:
        return None, "residencia inválida"

    fecha_cumpleanos = _get_payload_birthday(payload)

    # hashear siempre
    hashed = generate_password_hash(contrasena, method="pbkdf2:sha256")

    u = Usuario(
       nombre=nombre,
       correo=correo,
       **{"contraseña": hashed},
       rol_id=rol.id_rol,
       **{"fecha_cumpleaños": fecha_cumpleanos}, 
       estado=estado,
       residencia=residencia,
       pabellon=(payload.get("pabellon") or "").strip() or None,
       habitacion=(payload.get("habitacion") or "").strip() or None,
   )

    db.session.add(u)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return None, "No se pudo crear el usuario (verifica correo único)"
    return u, None


def listar_usuarios_admin(
    nombre: Optional[str] = None,
    rol: Optional[str] = None,  # slug
    estado: Optional[str] = None,
    residencia: Optional[str] = None,
    fecha_registro_desde: Optional[str] = None,
    fecha_registro_hasta: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
):
    q = Usuario.query

    if nombre:
        q = q.filter(Usuario.nombre.ilike(f"%{nombre.strip()}%"))

    if rol:
        r = _get_rol_by_slug(rol)
        if not r:
            return q.filter(False).paginate(page=page, per_page=per_page, error_out=False), None
        q = q.filter(Usuario.rol_id == r.id_rol)

    if estado:
        if estado not in ESTADOS_PERMITIDOS:
            return None, "estado inválido"
        q = q.filter(Usuario.estado == estado)

    if residencia:
        if residencia not in RESIDENCIAS_PERMITIDAS:
            return None, "residencia inválida"
        q = q.filter(Usuario.residencia == residencia)

    f_desde = _parse_fecha(fecha_registro_desde)
    f_hasta = _parse_fecha(fecha_registro_hasta)
    if f_desde:
        q = q.filter(func.date(Usuario.fecha_registro) >= f_desde)
    if f_hasta:
        q = q.filter(func.date(Usuario.fecha_registro) <= f_hasta)

    q = q.order_by(Usuario.fecha_registro.desc())
    pag = q.paginate(page=page, per_page=per_page, error_out=False)
    return pag, None


def obtener_usuario_admin(id_usuario: int) -> Optional[Usuario]:
    return Usuario.query.get(id_usuario)


def actualizar_usuario_admin(id_usuario: int, payload: dict) -> Tuple[Optional[Usuario], Optional[str]]:
    u = Usuario.query.get(id_usuario)
    if not u:
        return None, "Usuario no encontrado"

    if "nombre" in payload:
        nombre = (payload.get("nombre") or "").strip()
        if not nombre:
            return None, "nombre no puede ser vacío"
        u.nombre = nombre

    if "correo" in payload:
        correo = (payload.get("correo") or "").strip()
        if not correo:
            return None, "correo no puede ser vacío"
        u.correo = correo

    # contraseña (opcional)
    if "contrasena" in payload or "contraseña" in payload:
        nueva = _get_payload_password(payload)
        if not nueva:
            return None, "contrasena no puede ser vacía"
        hashed = generate_password_hash(nueva, method="pbkdf2:sha256")
        setattr(u, "contraseña", hashed)

    if "rol" in payload:
        rol_slug = (payload.get("rol") or "").strip()
        if not rol_slug:
            return None, "rol no puede ser vacío"
        rol_obj = _get_rol_by_slug(rol_slug)
        if not rol_obj:
            return None, "rol inválido"
        u.rol_id = rol_obj.id_rol

    if "estado" in payload:
        estado = (payload.get("estado") or "").strip() or None
        if estado and estado not in ESTADOS_PERMITIDOS:
            return None, "estado inválido"
        u.estado = estado

    if "residencia" in payload:
        residencia = (payload.get("residencia") or "").strip() or None
        if residencia and residencia not in RESIDENCIAS_PERMITIDAS:
            return None, "residencia inválida"
        u.residencia = residencia

    if "pabellon" in payload:
        u.pabellon = (payload.get("pabellon") or "").strip() or None

    if "habitacion" in payload:
        u.habitacion = (payload.get("habitacion") or "").strip() or None

    if "fecha_cumpleanos" in payload or "fecha_cumpleaños" in payload:
        setattr(u, "fecha_cumpleaños", _get_payload_birthday(payload))

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return None, "No se pudo actualizar el usuario (verifica correo único)"
    return u, None


def cambiar_estado_usuario_admin(id_usuario: int, nuevo_estado: str) -> Tuple[Optional[Usuario], Optional[str]]:
    u = Usuario.query.get(id_usuario)
    if not u:
        return None, "Usuario no encontrado"

    nuevo = (nuevo_estado or "").strip()
    if not nuevo:
        return None, "estado es requerido"
    if nuevo not in ESTADOS_PERMITIDOS:
        return None, "estado inválido"

    u.estado = nuevo
    db.session.commit()
    return u, None


# ===========================
# ENDPOINTS (Postman)
# ===========================

@administrar_bp.route("/usuarios", methods=["POST"])
def api_crear_usuario():
    payload = request.get_json(silent=True) or {}
    u, err = crear_usuario_admin(payload)
    if err:
        return jsonify({"message": err}), 400
    return jsonify(_usuario_to_dict(u)), 201


@administrar_bp.route("/usuarios", methods=["GET"])
def api_listar_usuarios():
    nombre = request.args.get("nombre")
    rol = request.args.get("rol")
    estado = request.args.get("estado")
    residencia = request.args.get("residencia")
    fecha_registro_desde = request.args.get("fecha_registro_desde")
    fecha_registro_hasta = request.args.get("fecha_registro_hasta")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    pag, err = listar_usuarios_admin(
        nombre=nombre,
        rol=rol,
        estado=estado,
        residencia=residencia,
        fecha_registro_desde=fecha_registro_desde,
        fecha_registro_hasta=fecha_registro_hasta,
        page=page,
        per_page=per_page,
    )
    if err:
        return jsonify({"message": err}), 400

    return jsonify({
        "items": [_usuario_to_dict(u) for u in pag.items],
        "page": pag.page,
        "per_page": pag.per_page,
        "total": pag.total,
        "pages": pag.pages,
    }), 200


@administrar_bp.route("/usuarios/<int:id_usuario>", methods=["GET"])
def api_obtener_usuario(id_usuario: int):
    u = obtener_usuario_admin(id_usuario)
    if not u:
        return jsonify({"message": "Usuario no encontrado"}), 404
    return jsonify(_usuario_to_dict(u)), 200


@administrar_bp.route("/usuarios/<int:id_usuario>", methods=["PATCH"])
def api_actualizar_usuario(id_usuario: int):
    payload = request.get_json(silent=True) or {}
    u, err = actualizar_usuario_admin(id_usuario, payload)
    if err:
        return jsonify({"message": err}), 400
    return jsonify(_usuario_to_dict(u)), 200


@administrar_bp.route("/usuarios/<int:id_usuario>/estado", methods=["PATCH"])
def api_cambiar_estado(id_usuario: int):
    payload = request.get_json(silent=True) or {}
    nuevo_estado = payload.get("estado")
    u, err = cambiar_estado_usuario_admin(id_usuario, nuevo_estado)
    if err:
        return jsonify({"message": err}), 400
    return jsonify(_usuario_to_dict(u)), 200