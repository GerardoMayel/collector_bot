# app/routes/main.py
from flask import Blueprint, render_template, request, jsonify, session
from http import HTTPStatus
from ..services.gemini_service import GeminiService
from flask import current_app
import asyncio
import logging
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.before_request
def before_request():
    # Asignar un ID de sesión si no existe
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/audio', methods=['POST'])
async def handle_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({
                'error': 'No audio file provided'
            }), HTTPStatus.BAD_REQUEST
            
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        gemini_service = GeminiService(current_app.config.get('GEMINI_API_KEY'))
        success, response = await gemini_service.process_audio_input(
            audio_data, 
            session['session_id']
        )
        
        if not success:
            return jsonify({
                'warning': 'Audio no reconocido',
                'response': response
            }), HTTPStatus.OK
            
        return jsonify({
            'response': response
        }), HTTPStatus.OK
        
    except Exception as e:
        logging.error(f"Error processing audio: {str(e)}")
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@main_bp.route('/api/chat', methods=['POST'])
async def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'No message provided'
            }), HTTPStatus.BAD_REQUEST

        gemini_service = GeminiService(current_app.config.get('GEMINI_API_KEY'))
        response = await gemini_service.get_completion(
            data['message'],
            session['session_id']
        )

        return jsonify({
            'response': response,
            'type': 'text'
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@main_bp.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    try:
        # Generar nuevo ID de sesión
        session['session_id'] = str(uuid.uuid4())
        return jsonify({'status': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR