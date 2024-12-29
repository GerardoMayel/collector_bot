# app/services/gemini_service.py
import google.generativeai as genai
from flask import current_app
import logging
from typing import Optional, List, Dict, Tuple
import base64
import json
from .database_service import DatabaseService

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.db_service = DatabaseService()
        self.conversation_history = {}
        self.system_prompt = """Eres un asistente de cobranza profesional y empático que tiene acceso a la base de datos del banco. 
        Recibiras instrucciones o preguntas en audio o texto y responderas con texto.
        
        INSTRUCCIONES IMPORTANTES:
        1. Identificar al cliente por nombre o número de cliente/tarjeta
        2. Consultar y proporcionar información precisa sobre:
        - Saldos actuales
        - Pagos vencidos
        - Fechas de corte y pago
        - Pagos mínimos requeridos
        3. Ofrecer opciones de pago y regularización
        4. Mantener un tono profesional y empático

        Si es audio:
        5. Primero, SIEMPRE indica claramente lo que escuchaste en el audio parafraseado un resumen de lo entenido antes de dar la respuesta
        6. Si no puedes entender el audio o hay problemas, indícalo directamente
        7. Si entendiste el audio, proporciona una respuesta concisa y relevante
        8. NO emules una conversación completa
        9. NO uses placeholders como [Nombre] o [Monto]
        10. Muy relevante: Solo usa información real que puedas obtener del audio o la base de datos
        
        Información del cliente:
        - Datos básicos: {client_data}
        - Resumen del cliente: {client_summary}
        - Próximos pagos: {next_payments}
        - Estado de mora: {mora_status}
        
        Historial de conversación, este historial se genera de conversaciones de propmts pasados:
        {conversation_history}
        """

    def _get_client_context(self, numero_cliente: Optional[str] = None, numero_tarjeta: Optional[str] = None) -> Dict:
        """Obtiene el contexto completo del cliente"""
        client_data = self.db_service.get_client_info(numero_cliente, numero_tarjeta)
        
        context_data = {
            'client_data': json.dumps(client_data, indent=2, ensure_ascii=False) if client_data else "No hay datos básicos del cliente",
            'client_summary': "No aplica" if not numero_cliente else json.dumps(
                self.db_service.get_client_summary(numero_cliente), 
                indent=2, 
                ensure_ascii=False
            ),
            'next_payments': "No aplica" if not numero_cliente else json.dumps(
                self.db_service.get_next_payments(numero_cliente), 
                indent=2, 
                ensure_ascii=False
            ),
            'mora_status': json.dumps(
                self.db_service.get_mora_status(numero_cliente, numero_tarjeta),
                indent=2,
                ensure_ascii=False
            )
        }
        
        return context_data

    def _get_conversation_history(self, session_id: str) -> str:
        """Obtiene el historial de conversación formateado"""
        if session_id not in self.conversation_history:
            return "No hay historial previo"
            
        history = []
        for msg in self.conversation_history[session_id]:
            role = "Usuario" if msg["role"] == "user" else "Asistente"
            history.append(f"{role}: {msg['content']}")
            
        return "\n".join(history)

    async def process_audio_input(self, audio_data: bytes, session_id: str) -> Tuple[bool, str]:
        """Procesa entrada de audio usando Gemini"""
        try:
            # Obtener el contexto actual de la conversación
            context_data = self._get_client_context(None, None)  # Inicialmente sin cliente identificado
            context_data['conversation_history'] = self._get_conversation_history(session_id)
            
            # Crear el contenido multimodal con el contexto
            prompt_parts = [
                {"text": self.system_prompt.format(**context_data)},
                {
                    "inline_data": {
                        "mime_type": "audio/wav",
                        "data": base64.b64encode(audio_data).decode('utf-8')
                    }
                }
            ]

            # Generar respuesta
            response = await self.model.generate_content_async(
                prompt_parts,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )

            if not response or not response.text:
                return False, "No se pudo procesar el audio."

            response_text = response.text.strip()
            
            # Guardar en el historial
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
                
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": response_text
            })
            
            return True, response_text

        except Exception as e:
            logging.error(f"Error en procesamiento de audio: {str(e)}")
            return False, f"Error al procesar el audio: {str(e)}"

    async def get_completion(
        self,
        user_message: str,
        session_id: str
    ) -> str:
        try:
            # Extraer información del cliente
            numero_cliente, numero_tarjeta = self.db_service.extract_client_info(user_message)
            
            # Obtener contexto completo
            context_data = self._get_client_context(numero_cliente, numero_tarjeta)
            context_data['conversation_history'] = self._get_conversation_history(session_id)
            
            # Preparar el contexto completo con todas las variables necesarias
            context = self.system_prompt.format(**context_data)
            
            # Agregar el mensaje actual
            context += f"\nUsuario: {user_message}\nAsistente:"

            # Generar respuesta
            response = await self.model.generate_content_async(
                context,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )

            if not response.text:
                raise Exception("No se pudo generar una respuesta válida")

            response_text = response.text.strip()
            
            # Guardar en el historial
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
                
            self.conversation_history[session_id].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response_text}
            ])

            return response_text

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
                generation_config={"temperature": 0.3}
            )

            return response.text.strip()

        except Exception as e:
            logging.error(f"Error en structured completion: {str(e)}")
            raise