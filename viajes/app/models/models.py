from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base

class Viaje(Base):
    """
    Entidad Viaje para el microservicio de viajes.
    Representa una ruta programada por un estudiante o profesor con su vehículo.
    """
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ID lógico del usuario conductor (en el microservicio de Usuarios)
    conductor_id = Column(Integer, nullable=False, index=True)
    conductor_nombre = Column(String(100), nullable=True) # Nombre visible del conductor
    
    # Datos de la ruta
    origen = Column(String(150), nullable=False, index=True)
    destino = Column(String(150), nullable=False, index=True)
    fecha_hora_salida = Column(DateTime, nullable=False)
    descripcion_ruta = Column(String(255), nullable=True)
    
    # Capacidad y costos
    cupos_totales = Column(Integer, nullable=False)
    cupos_disponibles = Column(Integer, nullable=False)
    aporte_sugerido = Column(Float, nullable=False, default=0.0) # Aporte solidario COP
    
    # Vehículo
    tipo_vehiculo = Column(String(20), nullable=False, default="carro") # "carro" o "moto"
    placa_vehiculo = Column(String(15), nullable=True)
    
    # Estado del viaje: PROGRAMADO, EN_CURSO, COMPLETADO, CANCELADO
    estado = Column(String(20), nullable=False, default="PROGRAMADO")
    
    # Marcas de tiempo
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
