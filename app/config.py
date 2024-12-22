# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener la ruta base del proyecto
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Configuración de Base de Datos con ruta absoluta
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "data", "cobranza.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # Configuración de caché
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300