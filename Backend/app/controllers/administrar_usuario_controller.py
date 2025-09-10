from typing import Optional, Tuple, List
from werkzeug.security import generate_password_hash
from sqlalchemy import and_, or_
from app import db
from app.models.usuarios import Usuario, ROLES_PERMITIDOS, ESTADOS_PERMITIDOS, RESIDENCIAS_PERMITIDAS


def _validar_rol(rol: str) -> bool:
    return rol in ROLES_PERMITIDOS

def _validar_estado(estado: str) -> bool:
    return estado in ESTADOS_PERMITIDOS

def _validar_residencia(res: Optional[str]) -> bool:
    return (res is None) or (res in RESIDENCIAS_PERMITIDAS)


# === Crear usuario ===
def crear_usuario_admin(payload: dict) -> Tuple[Optional[Usuario], Optional[str]]:
    """
    payload esperado:
    {
        "nombre": "...", "correo": "...",
        "contraseña": "...", "rol": "alumno|admin|psicologia|social",
        "fecha_cumpleaños": "YYYY-MM-DD" (opcional),
        "estado": "activo|inactivo" (opcional, default activo),
        "residencia": "Ciudad|Tello" (opcional),
        "pabellon": "A", "habitacion": "101" (opcionales)
    }
    """
    nombre = (payload.get("nombre") or "").strip()
    correo = (payload.get("correo") or "").strip().lower()
    contraseña = payload.get("contraseña")
    rol = (payload.get("rol") or "").strip()
    fecha_cumpleaños = payload.get("fecha_cumpleaños")
    estado = (payload.get("estado") or "activo").strip()
    residencia = payload.get("residencia")
    pabellon = payload.get("pabellon")
    habitacion = payload.get("habitacion")

    if not nombre or not correo or not contraseña or not rol:
        return None, "nombre, correo, contraseña y rol son obligatorios."

    if not _validar_rol(rol):
        return None, f"Rol inválido. Permitidos: {', '.join(ROLES_PERMITIDOS)}."

    if not _validar_estado(estado):
        return None, f"Estado inválido. Permitidos: {', '.join(ESTADOS_PERMITIDOS)}."

    if not _validar_residencia(residencia):
        return None, "Residencia inválida. Permitidos: Ciudad, Tello, o vacío."

    existente = Usuario.query.filter_by(correo=correo).first()
    if existente:
        return None, "El correo ya está registrado."

    nuevo = Usuario(
        nombre=nombre,
        correo=correo,
        contraseña=generate_password_hash(contraseña, method='pbkdf2:sha256'),
        rol=rol,
        estado=estado,
        residencia=residencia,
        pabellon=pabellon,
        habitacion=habitacion
    )

    # fecha_cumpleaños opcional
    if fecha_cumpleaños:
        try:
            from datetime import datetime
            nuevo.fecha_cumpleaños = datetime.strptime(fecha_cumpleaños, "%Y-%m-%d").date()
        except ValueError:
            return None, "fecha_cumpleaños debe tener formato YYYY-MM-DD."

    db.session.add(nuevo)
    db.session.commit()
    return nuevo, None


# === Listar con filtros y paginación ===
def listar_usuarios_admin(
    nombre: Optional[str] = None,
    rol: Optional[str] = None,
    estado: Optional[str] = None,
    residencia: Optional[str] = None,
    fecha_registro_desde: Optional[str] = None,  # "YYYY-MM-DD"
    fecha_registro_hasta: Optional[str] = None,  # "YYYY-MM-DD"
    page: int = 1,
    per_page: int = 50,
):
    q = Usuario.query

    if nombre:
        like = f"%{nombre.strip()}%"
        q = q.filter(Usuario.nombre.ilike(like))

    if rol:
        q = q.filter(Usuario.rol == rol.strip())

    if estado:
        q = q.filter(Usuario.estado == estado.strip())

    if residencia:
        q = q.filter(Usuario.residencia == residencia.strip())

    # Rango por fecha_registro (incluyente)
    from datetime import datetime, timedelta
    if fecha_registro_desde:
        try:
            dt_desde = datetime.strptime(fecha_registro_desde, "%Y-%m-%d")
            q = q.filter(Usuario.fecha_registro >= dt_desde)
        except ValueError:
            return None, "fecha_registro_desde debe tener formato YYYY-MM-DD."

    if fecha_registro_hasta:
        try:
            dt_hasta = datetime.strptime(fecha_registro_hasta, "%Y-%m-%d") + timedelta(days=1)
            q = q.filter(Usuario.fecha_registro < dt_hasta)
        except ValueError:
            return None, "fecha_registro_hasta debe tener formato YYYY-MM-DD."

    pag = q.order_by(Usuario.id_usuario.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return pag, None


# === Obtener uno ===
def obtener_usuario_admin(id_usuario: int) -> Optional[Usuario]:
    return Usuario.query.get(id_usuario)


# === Actualizar usuario (campos parciales) ===
def actualizar_usuario_admin(id_usuario: int, payload: dict) -> Tuple[Optional[Usuario], Optional[str]]:
    u = Usuario.query.get(id_usuario)
    if not u:
        return None, "Usuario no encontrado."

    # Campos editables
    nombre = payload.get("nombre")
    correo = payload.get("correo")
    rol = payload.get("rol")
    fecha_cumpleaños = payload.get("fecha_cumpleaños")
    estado = payload.get("estado")
    residencia = payload.get("residencia")
    pabellon = payload.get("pabellon")
    habitacion = payload.get("habitacion")

    if nombre is not None:
        u.nombre = nombre.strip() or u.nombre

    if correo is not None:
        correo = correo.strip().lower()
        if correo != u.correo:
            existe = Usuario.query.filter_by(correo=correo).first()
            if existe:
                return None, "El correo ya está registrado por otro usuario."
            u.correo = correo

    if contraseña:
        u.contraseña = generate_password_hash(contraseña, method='pbkdf2:sha256')

    if rol is not None:
        if not _validar_rol(rol):
            return None, f"Rol inválido. Permitidos: {', '.join(ROLES_PERMITIDOS)}."
        u.rol = rol

    if fecha_cumpleaños is not None:
        if fecha_cumpleaños == "":
            u.fecha_cumpleaños = None
        else:
            try:
                from datetime import datetime
                u.fecha_cumpleaños = datetime.strptime(fecha_cumpleaños, "%Y-%m-%d").date()
            except ValueError:
                return None, "fecha_cumpleaños debe tener formato YYYY-MM-DD."

    if estado is not None:
        if not _validar_estado(estado):
            return None, f"Estado inválido. Permitidos: {', '.join(ESTADOS_PERMITIDOS)}."
        u.estado = estado

    if residencia is not None:
        if not _validar_residencia(residencia):
            return None, "Residencia inválida. Permitidos: Ciudad, Tello, o vacío."
        u.residencia = residencia

    if pabellon is not None:
        u.pabellon = pabellon

    if habitacion is not None:
        u.habitacion = habitacion

    db.session.commit()
    return u, None


# === Cambiar estado rápido ===
def cambiar_estado_usuario_admin(id_usuario: int, nuevo_estado: str) -> Tuple[Optional[Usuario], Optional[str]]:
    if not _validar_estado(nuevo_estado):
        return None, f"Estado inválido. Permitidos: {', '.join(ESTADOS_PERMITIDOS)}."
    u = Usuario.query.get(id_usuario)
    if not u:
        return None, "Usuario no encontrado."
    u.estado = nuevo_estado
    db.session.commit()
    return u, None

