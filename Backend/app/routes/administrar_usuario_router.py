from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Tuple, Optional

from app import db
from app.models.usuarios import Usuario
from app.models.rol import Rol
from sqlalchemy import func

ESTADOS_PERMITIDOS = {"activo", "inactivo"}
RESIDENCIAS_PERMITIDAS = {"Ciudad", "Tello"}  

administrar_bp = Blueprint('administrar', __name__)

# ------------ helpers internos ------------
def _parse_fecha(d: Optional[str]) -> Optional[datetime.date]:
    if not d:
        return None
    # acepta 'YYYY-MM-DD'
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def _get_rol_by_slug(slug: Optional[str]) -> Optional[Rol]:
    if not slug:
        return None
    return Rol.query.filter(func.lower(Rol.slug) == slug.strip().lower()).first()


# ------------ casos de uso ------------
def crear_usuario_admin(payload: dict) -> Tuple[Optional[Usuario], Optional[str]]:
    """
    Crea un usuario. Espera al menos: nombre, correo, contrasena, rol (slug).
    Opcionales: fecha_cumpleanos (YYYY-MM-DD), estado, residencia, pabellon, habitacion.
    """
    nombre = (payload.get("nombre") or "").strip()
    correo = (payload.get("correo") or "").strip()
    contrasena = (payload.get("contrasena") or "").strip()
    rol_slug = (payload.get("rol") or "").strip()

    if not nombre:
        return None, "nombre es requerido"
    if not correo:
        return None, "correo es requerido"
    if not contrasena:
        return None, "contrasena es requerida"
    if not rol_slug:
        return None, "rol (slug) es requerido"

    # rol_id desde tabla roles
    rol = _get_rol_by_slug(rol_slug)
    if not rol:
        return None, "rol inválido"

    # validaciones opcionales
    estado = (payload.get("estado") or "").strip() or None
    if estado and ESTADOS_PERMITIDOS and estado not in ESTADOS_PERMITIDOS:
        return None, "estado inválido"

    residencia = (payload.get("residencia") or "").strip() or None
    if residencia and RESIDENCIAS_PERMITIDAS and residencia not in RESIDENCIAS_PERMITIDAS:
        return None, "residencia inválida"

    # fecha
    fecha_cumpleanos = _parse_fecha(payload.get("fecha_cumpleanos"))

    # crear
    u = Usuario(
        nombre=nombre,
        correo=correo,
        contrasena=contrasena,
        rol_id=rol.id_rol,
        fecha_cumpleanos=fecha_cumpleanos,
        estado=estado,
        residencia=residencia,
        pabellon=(payload.get("pabellon") or "").strip() or None,
        habitacion=(payload.get("habitacion") or "").strip() or None,
    )
    db.session.add(u)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # correo es unique; captura violación de unique genérica
        return None, "No se pudo crear el usuario (verifica correo único)"
    return u, None


def listar_usuarios_admin(
    nombre: Optional[str] = None,
    rol: Optional[str] = None,              # slug
    estado: Optional[str] = None,
    residencia: Optional[str] = None,
    fecha_registro_desde: Optional[str] = None,
    fecha_registro_hasta: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
):
    """
    Devuelve paginate. Filtra por nombre (icontains), rol (slug), estado, residencia y rango de fecha_registro.
    """
    q = Usuario.query

    if nombre:
        patron = f"%{nombre.strip()}%"
        q = q.filter(Usuario.nombre.ilike(patron))

    if rol:
        r = _get_rol_by_slug(rol)
        if not r:
            # si rol no existe, devolvemos lista vacía sin error
            return q.filter(False).paginate(page=page, per_page=per_page, error_out=False), None
        q = q.filter(Usuario.rol_id == r.id_rol)

    if estado:
        if ESTADOS_PERMITIDOS and estado not in ESTADOS_PERMITIDOS:
            return None, "estado inválido"
        q = q.filter(Usuario.estado == estado)

    if residencia:
        if RESIDENCIAS_PERMITIDAS and residencia not in RESIDENCIAS_PERMITIDAS:
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

    # campos opcionales
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

    if "contrasena" in payload:
        contrasena = (payload.get("contrasena") or "").strip()
        if not contrasena:
            return None, "contrasena no puede ser vacía"
        u.contrasena = contrasena

    if "rol" in payload:
        rol_slug = (payload.get("rol") or "").strip()
        if not rol_slug:
            return None, "rol no puede ser vacío"
        rol = _get_rol_by_slug(rol_slug)
        if not rol:
            return None, "rol inválido"
        u.rol_id = rol.id_rol

    if "estado" in payload:
        estado = (payload.get("estado") or "").strip() or None
        if estado and ESTADOS_PERMITIDOS and estado not in ESTADOS_PERMITIDOS:
            return None, "estado inválido"
        u.estado = estado

    if "residencia" in payload:
        residencia = (payload.get("residencia") or "").strip() or None
        if residencia and RESIDENCIAS_PERMITIDAS and residencia not in RESIDENCIAS_PERMITIDAS:
            return None, "residencia inválida"
        u.residencia = residencia

    if "pabellon" in payload:
        u.pabellon = (payload.get("pabellon") or "").strip() or None

    if "habitacion" in payload:
        u.habitacion = (payload.get("habitacion") or "").strip() or None

    if "fecha_cumpleanos" in payload:
        u.fecha_cumpleanos = _parse_fecha(payload.get("fecha_cumpleanos"))

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
    if ESTADOS_PERMITIDOS and nuevo not in ESTADOS_PERMITIDOS:
        return None, "estado inválido"

    u.estado = nuevo
    db.session.commit()
    return u, None