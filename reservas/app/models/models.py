from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base

class Reserva(Base):
    """
    Entidad Reserva para el microservicio de reservas.
    Representa la solicitud y confirmación de uno o varios cupos por parte de un pasajero
    en un viaje programado dentro de UNIRIDE.

    Incluye datos de snapshot del viaje (origen, destino, conductor, fecha de salida)
    para permitir consultas resilientes (degradación elegante) incluso si el
    Microservicio de Viajes se encuentra temporalmente fuera de línea.
    """
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Referencias lógicas a los otros microservicios (Sin ForeignKey física por desacoplamiento de BD)
    viaje_id = Column(Integer, nullable=False, index=True)
    pasajero_id = Column(Integer, nullable=False, index=True)

    # Datos del pasajero
    pasajero_nombre = Column(String(100), nullable=True)
    pasajero_correo = Column(String(120), nullable=True)

    # Detalles de la reserva
    cupos_reservados = Column(Integer, nullable=False, default=1)
    punto_encuentro = Column(String(150), nullable=True)
    comentarios = Column(String(255), nullable=True)
    aporte_acordado = Column(Float, nullable=False, default=0.0) # Aporte solidario total en COP

    # Snapshot distribuido de los datos del viaje al momento de reservar
    origen_viaje = Column(String(150), nullable=True)
    destino_viaje = Column(String(150), nullable=True)
    fecha_hora_salida = Column(DateTime, nullable=True)
    conductor_nombre = Column(String(100), nullable=True)

    # Estado de la reserva: CONFIRMADA, CANCELADA, COMPLETADA
    estado = Column(String(20), nullable=False, default="CONFIRMADA", index=True)

    # Marcas de tiempo de auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
