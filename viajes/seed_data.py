"""
Script para poblar la base de datos PostgreSQL de viajes con datos realistas para UNIMINUTO.
"""
from datetime import datetime, timedelta
from app.core.database import SessionLocal, Base, engine
from app.models.models import Viaje

def seed():
    print("[*] Conectando a PostgreSQL y asegurando tablas...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existentes = db.query(Viaje).count()
    if existentes > 0:
        print(f"[*] Ya existen {existentes} viajes en la base de datos. Omitiendo seed inicial.")
        db.close()
        return

    ahora = datetime.utcnow()
    viajes_semilla = [
        Viaje(
            conductor_id=1,
            conductor_nombre="David Jerez (Estudiante Ing. Sistemas)",
            origen="Portal Norte (Estación)",
            destino="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=2),
            descripcion_ruta="Tomo Autonorte hasta la 100, luego Av. 68 y Calle 80.",
            cupos_totales=3,
            cupos_disponibles=3,
            aporte_sugerido=4000.0,
            tipo_vehiculo="carro",
            placa_vehiculo="KHY-421",
            estado="PROGRAMADO"
        ),
        Viaje(
            conductor_id=2,
            conductor_nombre="Prof. Claudia Andrea Vásquez",
            origen="Centro Comercial Plaza de las Américas (Kennedy)",
            destino="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=3),
            descripcion_ruta="Av. Boyacá directo hasta Calle 80 frente al Minuto de Dios.",
            cupos_totales=4,
            cupos_disponibles=4,
            aporte_sugerido=4500.0,
            tipo_vehiculo="carro",
            placa_vehiculo="UPZ-890",
            estado="PROGRAMADO"
        ),
        Viaje(
            conductor_id=3,
            conductor_nombre="Juan David Aldana (Estudiante)",
            origen="Suba Rincón",
            destino="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=1, minutes=30),
            descripcion_ruta="Av. Cali hasta Calle 80.",
            cupos_totales=1,
            cupos_disponibles=1,
            aporte_sugerido=3000.0,
            tipo_vehiculo="moto",
            placa_vehiculo="LKM-12F",
            estado="PROGRAMADO"
        ),
        Viaje(
            conductor_id=4,
            conductor_nombre="Jorge Luis Lozano (Estudiante)",
            origen="Soacha (Estación San Mateo)",
            destino="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=4),
            descripcion_ruta="Autopista Sur hacia Av. Boyacá y subo por Calle 80.",
            cupos_totales=3,
            cupos_disponibles=3,
            aporte_sugerido=5000.0,
            tipo_vehiculo="carro",
            placa_vehiculo="MNO-567",
            estado="PROGRAMADO"
        ),
        Viaje(
            conductor_id=5,
            conductor_nombre="Prof. Carlos Mendoza",
            origen="UNIMINUTO Sede Principal Calle 80",
            destino="Chía Centro (Retorno tarde)",
            fecha_hora_salida=ahora + timedelta(hours=6),
            descripcion_ruta="Salida por Calle 80, variante Cota hacia Chía.",
            cupos_totales=3,
            cupos_disponibles=3,
            aporte_sugerido=6000.0,
            tipo_vehiculo="carro",
            placa_vehiculo="BGT-333",
            estado="PROGRAMADO"
        ),
    ]

    for v in viajes_semilla:
        db.add(v)

    db.commit()
    print(f"[OK] {len(viajes_semilla)} viajes creados exitosamente en PostgreSQL!")
    db.close()

if __name__ == "__main__":
    seed()
