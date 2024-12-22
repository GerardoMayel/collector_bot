# app/routes/main.py
from flask import Blueprint, render_template, request, jsonify
from http import HTTPStatus
from ..services.openai_service import OpenAIService
from ..services.gemini_service import GeminiService
from flask import current_app
import asyncio

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'No message provided'
            }), HTTPStatus.BAD_REQUEST

        # Inicializar el servicio de Gemini
        gemini_service = GeminiService(current_app.config.get('GEMINI_API_KEY'))
        
        try:
            # Usar asyncio para manejar la llamada asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(gemini_service.get_completion(data['message']))
            loop.close()
        except Exception as e:
            # Fallback a OpenAI si Gemini falla
            openai_service = OpenAIService(current_app.config.get('OPENAI_API_KEY'))
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(openai_service.get_completion(data['message']))
            loop.close()

        return jsonify({
            'response': response,
            'type': 'text'
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@main_bp.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })