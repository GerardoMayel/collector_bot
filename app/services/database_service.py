# app/services/database_service.py
from app.models import db
from app.models.cliente_cuenta import ClienteCuenta
from typing import List, Optional, Dict, Tuple
import re

class DatabaseService:
    @staticmethod
    def get_client_info(numero_cliente: Optional[str] = None, numero_tarjeta: Optional[str] = None) -> List[Dict]:
        """
        Obtiene información del cliente por número de cliente o número de tarjeta
        """
        try:
            query = ClienteCuenta.query
            
            if numero_cliente:
                query = query.filter(ClienteCuenta.NUMERO_CLIENTE == numero_cliente)
            elif numero_tarjeta:
                query = query.filter(ClienteCuenta.NUMERO_TARJETA == numero_tarjeta)
            else:
                return []

            clientes = query.all()
            
            return [{
                'numero_cliente': c.NUMERO_CLIENTE,
                'nombre': c.NOMBRE_CLIENTE,
                'numero_tarjeta': c.NUMERO_TARJETA,
                'tipo_tarjeta': c.TIPO_TARJETA,
                'linea_credito': c.LINEA_CREDITO,
                'saldo_actual': c.SALDO_ACTUAL,
                'saldo_vencido': c.SALDO_VENCIDO,
                'fecha_corte': c.FECHA_CORTE.strftime('%Y-%m-%d'),
                'fecha_limite_pago': c.FECHA_LIMITE_PAGO.strftime('%Y-%m-%d'),
                'pagos_vencidos': c.PAGOS_VENCIDOS,
                'pago_minimo': c.PAGO_MINIMO,
                'pago_no_intereses': c.PAGO_PARA_NO_INTERESES,
                'tasa_interes': c.TASA_INTERES_ANUAL,
                'cat': c.CAT,
                'estatus': c.ESTATUS_CUENTA,
                'ultima_fecha_pago': c.ULTIMA_FECHA_PAGO.strftime('%Y-%m-%d')
            } for c in clientes]
        except Exception as e:
            print(f"Error al obtener información del cliente: {str(e)}")
            return []

    @staticmethod
    def extract_client_info(text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extrae el número de cliente o tarjeta del texto proporcionado
        """
        # Buscar número de cliente (8 dígitos)
        cliente_match = re.search(r'\b\d{8}\b', text)
        if cliente_match:
            return cliente_match.group(), None
            
        # Buscar número de tarjeta (16 dígitos, puede contener espacios)
        tarjeta_match = re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text)
        if tarjeta_match:
            # Limpiar espacios y guiones
            numero_tarjeta = re.sub(r'[\s-]', '', tarjeta_match.group())
            return None, numero_tarjeta
            
        return None, None