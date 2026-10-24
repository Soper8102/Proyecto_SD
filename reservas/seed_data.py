"""
Script para poblar la base de datos PostgreSQL de reservas con datos realistas para UNIMINUTO.
"""
from datetime import datetime, timedelta
from app.core.database import SessionLocal, Base, engine
from app.models.models import Reserva

def seed():
    print("[*] Conectando a PostgreSQL (uniride_reservas_db) y asegurando tablas...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existentes = db.query(Reserva).count()
    if existentes > 0:
        print(f"[*] Ya existen {existentes} reservas en la base de datos. Omitiendo seed inicial.")
        db.close()
        return

    ahora = datetime.utcnow()
    reservas_semilla = [
        Reserva(
            viaje_id=1,
            pasajero_id=10,
            pasajero_nombre="Laura Valentina Gómez (Estudiante Ing. Industrial)",
            pasajero_correo="laura.gomez@uniminuto.edu.co",
            cupos_reservados=1,
            punto_encuentro="Estación Calle 100 (Puente peatonal norte)",
            comentarios="Llevo maleta pequeña, estoy puntual.",
            aporte_acordado=4000.0,
            origen_viaje="Portal Norte (Estación)",
            destino_viaje="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=2),
            conductor_nombre="David Jerez (Estudiante Ing. Sistemas)",
            estado="CONFIRMADA"
        ),
        Reserva(
            viaje_id=1,
            pasajero_id=11,
            pasajero_nombre="Camilo Andrés Torres (Estudiante Comunicación)",
            pasajero_correo="camilo.torres@uniminuto.edu.co",
            cupos_reservados=1,
            punto_encuentro="Portal Norte (Entrada principal)",
            comentarios="Voy con chaqueta azul de la universidad.",
            aporte_acordado=4000.0,
            origen_viaje="Portal Norte (Estación)",
            destino_viaje="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=2),
            conductor_nombre="David Jerez (Estudiante Ing. Sistemas)",
            estado="CONFIRMADA"
        ),
        Reserva(
            viaje_id=2,
            pasajero_id=12,
            pasajero_nombre="Daniela Ospina (Estudiante Psicología)",
            pasajero_correo="daniela.ospina@uniminuto.edu.co",
            cupos_reservados=2,
            punto_encuentro="Bahía frente a Plaza de las Américas",
            comentarios="Reservé para mí y mi compañera de semestre.",
            aporte_acordado=9000.0,
            origen_viaje="Centro Comercial Plaza de las Américas (Kennedy)",
            destino_viaje="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=3),
            conductor_nombre="Prof. Claudia Andrea Vásquez",
            estado="CONFIRMADA"
        ),
        Reserva(
            viaje_id=4,
            pasajero_id=13,
            pasajero_nombre="Santiago Morales (Estudiante Ing. Civil)",
            pasajero_correo="santiago.morales@uniminuto.edu.co",
            cupos_reservados=1,
            punto_encuentro="Estación San Mateo (Puerta Sur)",
            comentarios="Tuve que cancelar porque me cambiaron la clase a virtual.",
            aporte_acordado=5000.0,
            origen_viaje="Soacha (Estación San Mateo)",
            destino_viaje="UNIMINUTO Sede Principal Calle 80",
            fecha_hora_salida=ahora + timedelta(hours=4),
            conductor_nombre="Jorge Luis Lozano (Estudiante)",
            estado="CANCELADA"
        ),
    ]

    for r in reservas_semilla:
        db.add(r)

    db.commit()
    print(f"[OK] {len(reservas_semilla)} reservas iniciales creadas exitosamente en PostgreSQL!")
    db.close()

if __name__ == "__main__":
    seed()
