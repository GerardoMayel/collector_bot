# app/services/gemini_service.py
import google.generativeai as genai
from flask import current_app
import logging
from typing import Optional, List, Dict, Tuple
import base64

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.system_prompt = """Eres un asistente de cobranza profesional y empático. recibiras instrucciones o preguntas en audio o texto y responderas con texto
        INSTRUCCIONES IMPORTANTES:
        1. Identificar al cliente por nombre o número de cliente
        2. Consultar y proporcionar información precisa sobre:
        - Saldos actuales
        - Pagos vencidos
        - Fechas de corte y pago
        - Pagos mínimos requeridos
        3. Ofrecer opciones de pago y regularización
        4. Mantener un tono profesional y empático
        Si es audio:
        5. Primero, SIEMPRE indica claramente lo que escuchaste en el audio antes de responder con texto lo que seria tu respuesta habitual
        6. Si no puedes entender el audio o hay problemas, indícalo directamente.
        7. Si entendiste el audio, proporciona una respuesta concisa y relevante.
        8. NO emules una conversación completa.
        9. NO uses placeholders como [Nombre] o [Monto].
        10. Muy relevante, Solo usa información real que puedas obtener del audio o la base de datos.
        
        Por ejemplo:
        - cuando es entrada de audio: Si no entiendes el audio: "No pude entender claramente el audio. ¿Podrías repetir tu mensaje?"
        - cuando es entrada de audio: Si lo entiendes: "Entendí que preguntaste sobre [transcripción exacta]. En respuesta: [respuesta concisa]"
        - cuando es entrada de texto: En respuesta: [respuesta concisa] no es necesario repetir lo que entendiste esto solo es necesario en entrada de audio"
        """

    async def process_audio_input(self, audio_data: bytes) -> Tuple[bool, str]:
        """
        Procesa entrada de audio usando Gemini y retorna (éxito, respuesta)
        """
        try:
            # Crear el contenido multimodal con el contexto
            prompt_parts = [
                {"text": self.system_prompt},
                {
                    "inline_data": {
                        "mime_type": "audio/wav",
                        "data": base64.b64encode(audio_data).decode('utf-8')
                    }
                }
            ]

            # Configurar los parámetros de generación
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            # Generar respuesta
            response = await self.model.generate_content_async(
                prompt_parts,
                generation_config=generation_config
            )

            if not response or not response.text:
                return False, "No se pudo procesar el audio."

            # Procesar la respuesta
            response_text = response.text.strip()
            if "no pude entender" in response_text.lower() or "no se pudo entender" in response_text.lower():
                return False, response_text
                
            return True, response_text

        except Exception as e:
            logging.error(f"Error en procesamiento de audio: {str(e)}")
            return False, f"Error al procesar el audio: {str(e)}"

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