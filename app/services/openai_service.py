# app/services/openai_service.py
from openai import OpenAI
from flask import current_app
import logging

class OpenAIService:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = """Eres un asistente de cobranza profesional y empático. Tu objetivo es ayudar a los clientes 
        a regularizar sus pagos de tarjetas de crédito. Tienes acceso a la información real de sus cuentas y debes:

        1. Identificar al cliente por nombre o número de cliente
        2. Consultar y proporcionar información precisa sobre:
        - Saldos actuales
        - Pagos vencidos
        - Fechas de corte y pago
        - Pagos mínimos requeridos
        3. Ofrecer opciones de pago y regularización
        4. Mantener un tono profesional y empático

        Toda la información debe basarse en los datos reales de la base de datos."""

    async def get_completion(self, user_message, conversation_history=None):
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error en OpenAI service: {str(e)}")
            raise