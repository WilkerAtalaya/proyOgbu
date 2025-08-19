from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from dotenv import load_dotenv
from flask_cors import CORS

import os

# Carga variables de entorno
load_dotenv()

# Inicializa extensiones
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app) 

    # Inicializa extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Importación de modelos (para que SQLAlchemy los registre)
    from app.models import usuarios, anuncio, reconocimiento, queja, actividad, permisos, cita, asistencia, inscripcion

    # Registro de Blueprints
    from app.routes.usuarios import usuarios_bp
    from app.routes.anuncio_routes import anuncio_bp
    from app.routes.queja_routes import queja_bp
    from app.routes.reconocimiento_routes import reconocimiento_bp
    from app.routes.actividad_routes import actividad_bp
    from app.routes.permisos_routes import permisos_bp
    from app.routes.cita_routes import cita_bp
    from app.routes.asistencia_routes import asistencia_bp
    from app.files.routes import files_bp


    app.register_blueprint(usuarios_bp)
    app.register_blueprint(anuncio_bp)
    app.register_blueprint(queja_bp)
    app.register_blueprint(reconocimiento_bp)
    app.register_blueprint(actividad_bp)
    app.register_blueprint(permisos_bp)
    app.register_blueprint(cita_bp)
    app.register_blueprint(asistencia_bp)
    app.register_blueprint(files_bp)
    return app
