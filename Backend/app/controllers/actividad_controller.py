from app.models.actividad import Actividad
from app.models.inscripcion import InscripcionActividad
from app.models.usuarios import Usuario
from app import db
from datetime import datetime, date, time, timezone
from flask import request, jsonify
from app.files.service import save_upload

MAX_STOCK = 500
BUCKET = 'actividades'

def crear_actividad_con_archivo(aprobado_por_admin=False):
    # 1) datos del formulario
    tipo        = request.form.get('tipo')
    titulo      = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    fecha_raw   = request.form.get('fecha_actividad')
    hora_raw    = request.form.get('hora_actividad')
    stock_raw   = request.form.get('stock')
    id_usuario  = request.form.get('id_usuario')

    # 2) validar fecha/hora
    try:
        d = datetime.strptime(fecha_raw, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return jsonify({'error': 'Formato de fecha_actividad inválido (YYYY-MM-DD)'}), 400

    if hora_raw:
        try:
            hh, mm = map(int, hora_raw.split(':'))
            h = time(hh, mm)
        except Exception:
            return jsonify({'error': 'Formato de hora_actividad inválido (HH:MM)'}), 400
    else:
        h = time.min

    fecha_actividad_utc = datetime.combine(d, h)
    
    fecha_hoy_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if fecha_actividad_utc < fecha_hoy_utc:
        return jsonify({'error': 'La fecha de la actividad no puede estar en el pasado'}), 400

    # 3) validar stock
    try:
        stock = int(stock_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Stock debe ser un número entero'}), 400
    if not (1 <= stock <= MAX_STOCK):
        return jsonify({'error': f'Stock debe estar entre 1 y {MAX_STOCK}'}), 400

    # 4) archivo (opcional) usando servicio
    archivo_name = None
    if 'archivo' in request.files and request.files['archivo'].filename:
        meta, err = save_upload(request.files['archivo'], BUCKET, modes=('images','docs'))
        if err:
            return jsonify({'error': f'Archivo no permitido ({err})'}), 400
        archivo_name = meta['stored_name']

    nueva = Actividad(
        tipo=tipo,
        titulo=titulo,
        descripcion=descripcion,
        fecha_actividad=fecha_actividad_utc,
        archivo=archivo_name,   # guardamos solo el nombre
        id_usuario=id_usuario,
        stock=stock,
        estado='Aprobado' if aprobado_por_admin else 'Pendiente'
    )
    db.session.add(nueva)
    db.session.commit()
    return nueva

def listar_por_usuario(id_usuario):
    return Actividad.query.filter_by(id_usuario=id_usuario).order_by(Actividad.fecha_solicitud.desc()).all()

def listar_todas():
    return db.session.query(Actividad).join(Actividad.usuario).filter(Usuario.rol == 'alumno').order_by(Actividad.fecha_solicitud.desc()).all()

def cambiar_estado(id_actividad, nuevo_estado, motivo=None):
    a = Actividad.query.get(id_actividad)
    if not a:
        return None
    a.estado = nuevo_estado
    a.motivo_cancelacion = (motivo or '').strip() or None if nuevo_estado == 'Cancelado' else None
    db.session.commit()
    return a

def listar_aprobadas(excluir_usuario_id: int | None = None):
    hoy = date.today()
    acts = Actividad.query.filter_by(estado='Aprobado').all()

    actualizadas, mostrables = [], []
    for a in acts:
        if a.fecha_actividad.date() < hoy:
            a.estado = 'Finalizado'
            actualizadas.append(a)
        else:
            mostrables.append(a)
    if actualizadas:
        db.session.commit()

    if excluir_usuario_id:
        ids_inscritas = {
            row[0] for row in db.session.query(InscripcionActividad.id_actividad)
                                        .filter(InscripcionActividad.id_usuario == excluir_usuario_id).all()
        }
        mostrables = [a for a in mostrables if a.id_actividad not in ids_inscritas and a.id_usuario != excluir_usuario_id]

    mostrables.sort(key=lambda x: x.fecha_actividad)
    return mostrables

def inscribir_alumno(id_actividad, id_usuario):
    a = Actividad.query.get(id_actividad)
    if not a or a.estado != 'Aprobado':
        return jsonify({'error': 'Actividad no encontrada o no aprobada'}), 404

    u = Usuario.query.get(id_usuario)
    if not u or u.rol != 'alumno':
        return jsonify({'error': 'Solo los estudiantes pueden inscribirse'}), 403

    if InscripcionActividad.query.filter_by(id_actividad=id_actividad, id_usuario=id_usuario).first():
        return jsonify({'error': 'Ya inscrito'}), 409

    if InscripcionActividad.query.filter_by(id_actividad=id_actividad).count() >= a.stock:
        return jsonify({'error': 'Cupos agotados'}), 409

    db.session.add(InscripcionActividad(id_actividad=id_actividad, id_usuario=id_usuario))
    db.session.commit()
    return jsonify({'mensaje': 'Inscripción exitosa'}), 201

def cancelar_inscripcion(id_actividad, id_usuario):
    u = Usuario.query.get(id_usuario)
    if not u or u.rol != 'alumno':
        return jsonify({'error': 'Solo los estudiantes pueden cancelar'}), 403

    insc = InscripcionActividad.query.filter_by(id_actividad=id_actividad, id_usuario=id_usuario).first()
    if not insc:
        return jsonify({'error': 'Inscripción no encontrada'}), 404

    db.session.delete(insc)
    db.session.commit()
    return jsonify({'mensaje': 'Inscripción cancelada'}), 200

def listar_actividades_inscritas_por_usuario(id_usuario):
    q = (db.session.query(InscripcionActividad, Actividad)
         .join(Actividad, Actividad.id_actividad == InscripcionActividad.id_actividad)
         .filter(InscripcionActividad.id_usuario == id_usuario)
         .order_by(InscripcionActividad.fecha_registro.desc()))
    return q.all()

def listar_inscritos_de_actividad(id_actividad):
    q = (db.session.query(InscripcionActividad, Usuario)
         .join(Usuario, Usuario.id_usuario == InscripcionActividad.id_usuario)
         .filter(InscripcionActividad.id_actividad == id_actividad)
         .order_by(InscripcionActividad.fecha_registro.desc()))
    return q.all()
