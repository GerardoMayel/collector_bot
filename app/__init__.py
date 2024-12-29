# app/__init__.py
from flask import Flask
from flask_cors import CORS
from .config import Config
from .models import db
from .database.init_db import init_db

def create_app(config_class=Config):
    # Configura la aplicación con las rutas correctas para archivos estáticos
    app = Flask(__name__,
                static_url_path='',
                static_folder='static',
                template_folder='templates')
    
    # Cargar configuración
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    CORS(app)
    db.init_app(app)
    
    # Inicializar la base de datos
    init_db(app)
    
    # Registrar blueprints
    from .routes.main import main_bp
    app.register_blueprint(main_bp)
    
    # Configurar manejo de errores para producción
    if not app.debug:
        @app.errorhandler(500)
        def internal_error(error):
            return render_template('errors/500.html'), 500

        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('errors/404.html'), 404
    
    return app