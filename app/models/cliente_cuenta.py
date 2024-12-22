# app/models/cliente_cuenta.py
from . import db
from datetime import datetime

class ClienteCuenta(db.Model):
    __tablename__ = 'CLIENTE_CUENTAS'
    
    ID = db.Column(db.Integer, primary_key=True)
    NUMERO_CLIENTE = db.Column(db.String(8), nullable=False)
    NOMBRE_CLIENTE = db.Column(db.String(100), nullable=False)
    NUMERO_TARJETA = db.Column(db.String(16), nullable=False)
    TIPO_TARJETA = db.Column(db.String(50), nullable=False)
    LINEA_CREDITO = db.Column(db.Float, nullable=False)
    SALDO_ACTUAL = db.Column(db.Float, nullable=False)
    SALDO_VENCIDO = db.Column(db.Float, default=0.0)
    FECHA_CORTE = db.Column(db.Date, nullable=False)
    FECHA_LIMITE_PAGO = db.Column(db.Date, nullable=False)
    PAGOS_VENCIDOS = db.Column(db.Integer, default=0)
    PAGO_MINIMO = db.Column(db.Float, nullable=False)
    PAGO_PARA_NO_INTERESES = db.Column(db.Float, nullable=False)
    TASA_INTERES_ANUAL = db.Column(db.Float, nullable=False)
    CAT = db.Column(db.Float, nullable=False)
    ESTATUS_CUENTA = db.Column(db.String(20), nullable=False)
    ULTIMA_FECHA_PAGO = db.Column(db.Date, nullable=True)