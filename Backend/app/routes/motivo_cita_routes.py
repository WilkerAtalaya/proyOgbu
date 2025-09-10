from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from app.models.motivo_cita import MotivoCita
from app.models.area import Area

motivo_cita_bp = Blueprint('motivo_cita', __name__)

@motivo_cita_bp.route('/motivos-cita', methods=['GET'])
def listar_motivos():
    """
    Parámetros opcionales:
    - q:   texto para buscar por 'motivo' (ilike)
    - area: nombre exacto del área (p.ej. Psicología)
    - id_area: id numérico de área
    """
    q = MotivoCita.query.join(Area, MotivoCita.id_area == Area.id_area)

    texto = request.args.get('q')
    if texto:
        q = q.filter(MotivoCita.motivo.ilike(f"%{texto}%"))

    area_nombre = request.args.get('area')
    if area_nombre:
        q = q.filter(Area.area == area_nombre)

    id_area = request.args.get('id_area', type=int)
    if id_area:
        q = q.filter(MotivoCita.id_area == id_area)

    motivos = q.order_by(MotivoCita.motivo.asc()).all()
    data = [{
        "id": m.id,
        "motivo": m.motivo,
        "id_area": m.id_area,
        "area": m.area_rel.area if m.area_rel else None
    } for m in motivos]
    return jsonify(data), 200

@motivo_cita_bp.route('/motivos-cita/<int:id_motivo>', methods=['GET'])
def detalle_motivo(id_motivo):
    m = MotivoCita.query.get(id_motivo)
    if not m:
        return jsonify({"error": "Motivo no encontrado"}), 404
    return jsonify({
        "id": m.id,
        "motivo": m.motivo,
        "id_area": m.id_area,
        "area": m.area_rel.area if m.area_rel else None
    }), 200
