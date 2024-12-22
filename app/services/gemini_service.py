# app/services/gemini_service.py
import google.generativeai as genai
from flask import current_app
import logging
from typing import Optional, List, Dict

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        genai.configure(api_key=api_key)
        # Usando el modelo más reciente gemini-2.0-flash-exp
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
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

    async def get_completion(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        try:
            # Configurar los parámetros de generación
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            # Preparar el contexto con el historial si existe
            context = f"{self.system_prompt}\n\n"
            if conversation_history:
                for message in conversation_history:
                    role = "Usuario: " if message["role"] == "user" else "Asistente: "
                    context += f"{role}{message['content']}\n"
            
            context += f"Usuario: {user_message}\nAsistente:"

            # Generar la respuesta
            response = await self.model.generate_content_async(
                context,
                generation_config=generation_config,
                stream=False
            )

            # Verificar si hay error en la respuesta
            if not response.candidates or not response.candidates[0].content.parts:
                raise Exception("No se pudo generar una respuesta válida")

            return response.candidates[0].content.parts[0].text.strip()

        except Exception as e:
            logging.error(f"Error en Gemini service: {str(e)}")
            raise

    async def get_structured_completion(
        self, 
        user_message: str,
        output_structure: dict
    ) -> dict:
        """
        Método para obtener respuestas estructuradas usando la capacidad de structured outputs
        """
        try:
            prompt = f"""
            {self.system_prompt}
            
            Basado en el siguiente mensaje del usuario, genera una respuesta estructurada
            siguiendo exactamente este formato: {output_structure}
            
            Mensaje del usuario: {user_message}
            """

            response = await self.model.generate_content_async(
                prompt,
                generation_config={"temperature": 0.3}  # Menor temperatura para respuestas más estructuradas
            )

            # Procesar y validar la respuesta estructurada
            return response.candidates[0].content.parts[0].text.strip()

        except Exception as e:
            logging.error(f"Error en structured completion: {str(e)}")
            raise