# app/routes/main.py
from flask import Blueprint, render_template, request, jsonify
from http import HTTPStatus

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
            
        # Aquí irá la lógica de procesamiento
        return jsonify({
            'response': 'Message received',
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