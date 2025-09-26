from flask import Blueprint, jsonify, request, g         # <- agrega g
from sqlalchemy import or_
from app.models.motivo_cita import MotivoCita
from app.models.area import Area
from app.models.usuarios import Usuario                  # <- importa Usuario

motivo_cita_bp = Blueprint('motivo_cita', __name__)

def _usuario_actual():
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user
    uid = request.args.get('id_usuario', type=int)
    if not uid:
        uid = request.form.get('id_usuario', type=int)
    if not uid:
        data = request.get_json(silent=True) or {}
        uid = data.get('id_usuario')
    return Usuario.query.get(uid) if uid else None

@motivo_cita_bp.route('/motivos-cita', methods=['GET'])
def listar_motivos():
    q = MotivoCita.query.join(Area, MotivoCita.id_area == Area.id_area)

    user = _usuario_actual()
    if user and user.rol_area_id:                     
        q = q.filter(MotivoCita.id_area == user.rol_area_id)
    else:
        id_area = request.args.get('id_area', type=int)
        if id_area:
            q = q.filter(MotivoCita.id_area == id_area)
        else:
            area_nombre = request.args.get('area')
            if area_nombre:
                q = q.filter(Area.area == area_nombre)

    # Búsqueda por texto
    texto = request.args.get('q')
    if texto:
        q = q.filter(MotivoCita.motivo.ilike(f"%{texto}%"))

    motivos = q.order_by(MotivoCita.motivo.asc()).all()
    data = [{
        "id": m.id,
        "motivo": m.motivo,
        "id_area": m.id_area,
        "area": m.area_rel.area if m.area_rel else None
    } for m in motivos]
    return jsonify(data), 200
