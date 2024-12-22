# app/database/init_db.py
from app.models import db
from app.models.cliente_cuenta import ClienteCuenta
from datetime import datetime, timedelta
import os

def init_db(app):
    # Obtener la ruta base del proyecto
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # Asegurarse que el directorio data existe
    data_dir = os.path.join(basedir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Directorio de datos creado en: {data_dir}")
    
    # Crear todas las tablas
    with app.app_context():
        db.create_all()
        print("Base de datos creada exitosamente")
        
        # Verificar si ya existen registros
        if ClienteCuenta.query.first() is None:
            print("Insertando datos de ejemplo...")
            # Crear registros de ejemplo
            clientes = [
                ClienteCuenta(
                    NUMERO_CLIENTE='12345678',
                    NOMBRE_CLIENTE='OSCAR HERNANDEZ',
                    NUMERO_TARJETA='4539123456789012',  # Formato VISA
                    TIPO_TARJETA='VISA PLATINUM',
                    LINEA_CREDITO=80000.00,
                    SALDO_ACTUAL=45000.00,
                    SALDO_VENCIDO=1500.00,
                    FECHA_CORTE=datetime.now().date() + timedelta(days=5),
                    FECHA_LIMITE_PAGO=datetime.now().date() + timedelta(days=20),
                    PAGOS_VENCIDOS=1,
                    PAGO_MINIMO=2250.00,
                    PAGO_PARA_NO_INTERESES=45000.00,
                    TASA_INTERES_ANUAL=39.99,
                    CAT=63.8,
                    ESTATUS_CUENTA='ACTIVA',
                    ULTIMA_FECHA_PAGO=datetime.now().date() - timedelta(days=35)
                ),
                ClienteCuenta(
                    NUMERO_CLIENTE='12345678',
                    NOMBRE_CLIENTE='OSCAR HERNANDEZ',
                    NUMERO_TARJETA='5412123456789012',  # Formato Mastercard
                    TIPO_TARJETA='MASTERCARD BLACK',
                    LINEA_CREDITO=150000.00,
                    SALDO_ACTUAL=25000.00,
                    SALDO_VENCIDO=0.00,
                    FECHA_CORTE=datetime.now().date() + timedelta(days=15),
                    FECHA_LIMITE_PAGO=datetime.now().date() + timedelta(days=30),
                    PAGOS_VENCIDOS=0,
                    PAGO_MINIMO=1250.00,
                    PAGO_PARA_NO_INTERESES=25000.00,
                    TASA_INTERES_ANUAL=36.99,
                    CAT=58.9,
                    ESTATUS_CUENTA='ACTIVA',
                    ULTIMA_FECHA_PAGO=datetime.now().date() - timedelta(days=5)
                ),
                ClienteCuenta(
                    NUMERO_CLIENTE='87654321',
                    NOMBRE_CLIENTE='GERARDO FERNANDEZ',
                    NUMERO_TARJETA='4024007123456789',  # Formato VISA
                    TIPO_TARJETA='VISA INFINITE',
                    LINEA_CREDITO=200000.00,
                    SALDO_ACTUAL=180000.00,
                    SALDO_VENCIDO=15000.00,
                    FECHA_CORTE=datetime.now().date() + timedelta(days=3),
                    FECHA_LIMITE_PAGO=datetime.now().date() + timedelta(days=18),
                    PAGOS_VENCIDOS=2,
                    PAGO_MINIMO=9000.00,
                    PAGO_PARA_NO_INTERESES=180000.00,
                    TASA_INTERES_ANUAL=42.99,
                    CAT=68.5,
                    ESTATUS_CUENTA='MORA',
                    ULTIMA_FECHA_PAGO=datetime.now().date() - timedelta(days=65)
                ),
                ClienteCuenta(
                    NUMERO_CLIENTE='87654321',
                    NOMBRE_CLIENTE='GERARDO FERNANDEZ',
                    NUMERO_TARJETA='5587123456789012',  # Formato Mastercard
                    TIPO_TARJETA='MASTERCARD PLATINUM',
                    LINEA_CREDITO=90000.00,
                    SALDO_ACTUAL=85000.00,
                    SALDO_VENCIDO=8500.00,
                    FECHA_CORTE=datetime.now().date() - timedelta(days=2),
                    FECHA_LIMITE_PAGO=datetime.now().date() + timedelta(days=13),
                    PAGOS_VENCIDOS=1,
                    PAGO_MINIMO=4250.00,
                    PAGO_PARA_NO_INTERESES=85000.00,
                    TASA_INTERES_ANUAL=40.99,
                    CAT=65.2,
                    ESTATUS_CUENTA='MORA',
                    ULTIMA_FECHA_PAGO=datetime.now().date() - timedelta(days=45)
                )
            ]
            
            db.session.add_all(clientes)
            db.session.commit()
            print("Datos de ejemplo insertados exitosamente")