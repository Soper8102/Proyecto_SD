from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class ViajeBase(BaseModel):
    origen: str = Field(..., min_length=3, max_length=150, description="Punto de origen de la ruta")
    destino: str = Field(..., min_length=3, max_length=150, description="Punto de destino de la ruta")
    fecha_hora_salida: datetime = Field(..., description="Fecha y hora de salida programada")
    cupos_totales: int = Field(..., gt=0, le=8, description="Número total de cupos ofrecidos")
    aporte_sugerido: float = Field(default=0.0, ge=0.0, description="Aporte solidario sugerido en COP")
    tipo_vehiculo: Literal["carro", "moto"] = Field(default="carro", description="Tipo de transporte")
    descripcion_ruta: Optional[str] = Field(None, max_length=255, description="Paradas intermedias o detalles")
    placa_vehiculo: Optional[str] = Field(None, max_length=15, description="Placa del vehículo")

class ViajeCreate(ViajeBase):
    conductor_id: int = Field(..., gt=0, description="ID del conductor en el servicio de usuarios")
    conductor_nombre: Optional[str] = Field(None, max_length=100, description="Nombre del conductor")

class ViajeUpdate(BaseModel):
    origen: Optional[str] = Field(None, min_length=3, max_length=150)
    destino: Optional[str] = Field(None, min_length=3, max_length=150)
    fecha_hora_salida: Optional[datetime] = None
    cupos_totales: Optional[int] = Field(None, gt=0, le=8)
    cupos_disponibles: Optional[int] = Field(None, ge=0)
    aporte_sugerido: Optional[float] = Field(None, ge=0.0)
    tipo_vehiculo: Optional[Literal["carro", "moto"]] = None
    descripcion_ruta: Optional[str] = None
    placa_vehiculo: Optional[str] = None
    estado: Optional[Literal["PROGRAMADO", "EN_CURSO", "COMPLETADO", "CANCELADO"]] = None

class ActualizarCuposRequest(BaseModel):
    """
    Utilizado por el microservicio de Reservas:
    - delta = -1 para reservar un cupo
    - delta = +1 para liberar un cupo al cancelar reserva
    """
    delta_cupos: int = Field(..., description="Cantidad a restar (negativo) o sumar (positivo) a los cupos")

class ViajeResponse(ViajeBase):
    id: int
    conductor_id: int
    conductor_nombre: Optional[str] = None
    cupos_disponibles: int
    estado: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MensajeResponse(BaseModel):
    mensaje: str
    detalles: Optional[dict] = None
