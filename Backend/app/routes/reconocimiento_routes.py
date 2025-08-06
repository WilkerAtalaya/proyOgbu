from flask import Blueprint, request, jsonify
from app.controllers.reconocimiento_controller import crear_reconocimiento, obtener_reconocimientos, buscar_alumnos_por_nombre

reconocimiento_bp = Blueprint("reconocimiento", __name__)

@reconocimiento_bp.route("/reconocimientos", methods=["POST"])
def crear():
    data = request.json
    reconocimiento = crear_reconocimiento(data)
    return jsonify({
        "id": reconocimiento.id_reconocimiento,
        "mensaje": "Reconocimiento creado correctamente"
    }), 201

@reconocimiento_bp.route("/reconocimientos", methods=["GET"])
def listar():
    reconocimientos = obtener_reconocimientos()
    return jsonify([
        {
            "id": r.id_reconocimiento,
            "id_alumno": r.id_alumno,
            "descripcion": r.descripcion,
            "fecha": r.fecha_reconocimiento.strftime('%Y-%m-%d'),
            "id_usuario": r.id_usuario
        } for r in reconocimientos
    ])

@reconocimiento_bp.route("/alumnos/buscar", methods=["GET"])
def buscar_alumnos():
    termino = request.args.get("q", "")
    if not termino:
        return jsonify([])

    alumnos = buscar_alumnos_por_nombre(termino)
    resultados = [
        {"id": alumno.id_usuario, "nombre": alumno.nombre, "correo": alumno.correo}
        for alumno in alumnos
    ]
    return jsonify(resultados)

