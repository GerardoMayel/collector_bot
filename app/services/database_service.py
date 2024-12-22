# app/services/database_service.py
from app.models.cliente_cuenta import ClienteCuenta

class DatabaseService:
    @staticmethod
    def get_client_accounts(numero_cliente=None, nombre_cliente=None):
        query = ClienteCuenta.query
        
        if numero_cliente:
            query = query.filter_by(NUMERO_CLIENTE=numero_cliente)
        if nombre_cliente:
            query = query.filter_by(NOMBRE_CLIENTE=nombre_cliente.upper())
            
        return query.all()

    @staticmethod
    def get_account_by_card(numero_tarjeta):
        return ClienteCuenta.query.filter_by(NUMERO_TARJETA=numero_tarjeta).first()