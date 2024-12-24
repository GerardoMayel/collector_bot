# app/services/database_service.py
from app.models import db
from app.models.cliente_cuenta import ClienteCuenta
from typing import List, Optional, Dict, Tuple
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import re

class DatabaseService:
    @staticmethod
    def get_client_info(numero_cliente: Optional[str] = None, numero_tarjeta: Optional[str] = None) -> List[Dict]:
        """Obtiene información básica del cliente"""
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
                'linea_credito': float(c.LINEA_CREDITO),
                'saldo_actual': float(c.SALDO_ACTUAL),
                'saldo_vencido': float(c.SALDO_VENCIDO),
                'fecha_corte': c.FECHA_CORTE.strftime('%Y-%m-%d'),
                'fecha_limite_pago': c.FECHA_LIMITE_PAGO.strftime('%Y-%m-%d'),
                'pagos_vencidos': int(c.PAGOS_VENCIDOS),
                'pago_minimo': float(c.PAGO_MINIMO),
                'pago_no_intereses': float(c.PAGO_PARA_NO_INTERESES),
                'tasa_interes': float(c.TASA_INTERES_ANUAL),
                'cat': float(c.CAT),
                'estatus': c.ESTATUS_CUENTA,
                'ultima_fecha_pago': c.ULTIMA_FECHA_PAGO.strftime('%Y-%m-%d')
            } for c in clientes]
        except Exception as e:
            print(f"Error al obtener información del cliente: {str(e)}")
            return []

    @staticmethod
    def get_client_summary(numero_cliente: str) -> Dict:
        """Obtiene un resumen consolidado de todas las tarjetas del cliente"""
        try:
            # Consulta para obtener agregaciones
            result = db.session.query(
                func.count(ClienteCuenta.NUMERO_TARJETA).label('total_tarjetas'),
                func.sum(ClienteCuenta.SALDO_ACTUAL).label('saldo_total'),
                func.sum(ClienteCuenta.SALDO_VENCIDO).label('saldo_vencido_total'),
                func.sum(ClienteCuenta.PAGO_MINIMO).label('pago_minimo_total'),
                func.sum(case([(ClienteCuenta.ESTATUS_CUENTA == 'MORA', 1)], else_=0)).label('tarjetas_mora')
            ).filter(ClienteCuenta.NUMERO_CLIENTE == numero_cliente).first()

            if not result:
                return {}

            return {
                'total_tarjetas': int(result.total_tarjetas or 0),
                'saldo_total': float(result.saldo_total or 0),
                'saldo_vencido_total': float(result.saldo_vencido_total or 0),
                'pago_minimo_total': float(result.pago_minimo_total or 0),
                'tarjetas_mora': int(result.tarjetas_mora or 0)
            }
        except Exception as e:
            print(f"Error al obtener resumen del cliente: {str(e)}")
            return {}

    @staticmethod
    def get_next_payments(numero_cliente: str) -> List[Dict]:
        """Obtiene las próximas fechas de pago de todas las tarjetas del cliente"""
        try:
            tarjetas = ClienteCuenta.query.filter(
                ClienteCuenta.NUMERO_CLIENTE == numero_cliente
            ).all()

            return [{
                'numero_tarjeta': t.NUMERO_TARJETA,
                'tipo_tarjeta': t.TIPO_TARJETA,
                'fecha_corte': t.FECHA_CORTE.strftime('%Y-%m-%d'),
                'fecha_limite_pago': t.FECHA_LIMITE_PAGO.strftime('%Y-%m-%d'),
                'pago_minimo': float(t.PAGO_MINIMO),
                'pago_no_intereses': float(t.PAGO_PARA_NO_INTERESES)
            } for t in tarjetas]
        except Exception as e:
            print(f"Error al obtener próximos pagos: {str(e)}")
            return []

    @staticmethod
    def get_mora_status(numero_cliente: Optional[str] = None, numero_tarjeta: Optional[str] = None) -> List[Dict]:
        """Obtiene el estado de mora de las tarjetas"""
        try:
            query = ClienteCuenta.query.filter(ClienteCuenta.ESTATUS_CUENTA == 'MORA')
            if numero_cliente:
                query = query.filter(ClienteCuenta.NUMERO_CLIENTE == numero_cliente)
            elif numero_tarjeta:
                query = query.filter(ClienteCuenta.NUMERO_TARJETA == numero_tarjeta)

            tarjetas_mora = query.all()
            return [{
                'numero_tarjeta': t.NUMERO_TARJETA,
                'tipo_tarjeta': t.TIPO_TARJETA,
                'saldo_vencido': float(t.SALDO_VENCIDO),
                'pagos_vencidos': int(t.PAGOS_VENCIDOS),
                'ultima_fecha_pago': t.ULTIMA_FECHA_PAGO.strftime('%Y-%m-%d')
            } for t in tarjetas_mora]
        except Exception as e:
            print(f"Error al obtener estado de mora: {str(e)}")
            return []

    @staticmethod
    def get_payment_status() -> Dict:
        """Obtiene estadísticas generales de pagos"""
        try:
            result = db.session.query(
                func.count(ClienteCuenta.NUMERO_TARJETA).label('total_tarjetas'),
                func.count(case([(ClienteCuenta.ESTATUS_CUENTA == 'MORA', 1)])).label('tarjetas_mora'),
                func.sum(ClienteCuenta.SALDO_VENCIDO).label('saldo_vencido_total')
            ).first()

            return {
                'total_tarjetas': int(result.total_tarjetas or 0),
                'tarjetas_mora': int(result.tarjetas_mora or 0),
                'saldo_vencido_total': float(result.saldo_vencido_total or 0)
            }
        except Exception as e:
            print(f"Error al obtener estadísticas de pagos: {str(e)}")
            return {}

    @staticmethod
    def extract_client_info(text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extrae el número de cliente o tarjeta del texto"""
        # Buscar número de cliente (8 dígitos)
        cliente_match = re.search(r'\b\d{8}\b', text)
        if cliente_match:
            return cliente_match.group(), None
            
        # Buscar número de tarjeta (16 dígitos, puede contener espacios)
        tarjeta_match = re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text)
        if tarjeta_match:
            numero_tarjeta = re.sub(r'[\s-]', '', tarjeta_match.group())
            return None, numero_tarjeta
            
        return None, None