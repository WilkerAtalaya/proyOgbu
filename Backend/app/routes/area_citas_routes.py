from flask import Blueprint, jsonify
from app.models.area import Area

area_bp = Blueprint('area', __name__)

@area_bp.route('/areas', methods=['GET'])
def listar_areas():
    filas = Area.query.order_by(Area.area.asc()).all()
    return jsonify([{"id_area": a.id_area, "area": a.area} for a in filas]), 200
