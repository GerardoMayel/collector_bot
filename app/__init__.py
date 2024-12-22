# app/__init__.py
from flask import Flask
from flask_cors import CORS
from .config import Config
from .models import db
from .database.init_db import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    CORS(app)
    db.init_app(app)
    
    # Inicializar la base de datos
    init_db(app)
    
    # Registrar blueprints
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    return app