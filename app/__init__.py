# app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar CORS
    CORS(app)
    
    # Registrar blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    return app