from flask import Blueprint, request, jsonify
from app import db
from app.models.usuarios import Usuario
from app.models.motivo_cita import MotivoCita
from app.models.area import Area

motivo_bp = Blueprint('motivo', __name__)

@motivo_bp.route('/motivos-cita', methods=['GET'])
def listar_motivos():
    """
    Casos:
      - ?id_usuario=10 -> usa su rol.area_id si existe
      - ?area_id=2     -> filtra por esa área
      - ninguno        -> devuelve todos
    Respuestas de error SIEMPRE como 400 con campo {"error": "..."} cuando aplique.
    """
    try:
        area_id = request.args.get('area_id', type=int)
        id_usuario = request.args.get('id_usuario', type=int)

        user = None
        rol_id = None

        if id_usuario:
            user = Usuario.query.get(id_usuario)
            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 400
            rol_id = getattr(user, 'rol_id', None)
            # Si no pasaron area_id y el usuario tiene un rol de área, usarlo
            if area_id is None and getattr(user, 'rol_area_id', None):
                area_id = user.rol_area_id

        q = MotivoCita.query
        if area_id is not None:
            existe = db.session.query(Area.id_area).filter_by(id_area=area_id).first()
            if not existe:
                return jsonify({"error": "area_id inválido"}), 400
            q = q.filter(MotivoCita.id_area == area_id)

        motivos = q.order_by(MotivoCita.motivo.asc()).all()
        data = [m.to_dict() for m in motivos]

        return jsonify({
            "rol_id": rol_id,             # puede ser None si no se pasó id_usuario
            "motivos": data
        }), 200

    except Exception as e:
        # último recurso: nunca revelar errores internos
        return jsonify({"error": "No se pudieron obtener los motivos"}), 400
