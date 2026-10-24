from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class ReservaBase(BaseModel):
    viaje_id: int = Field(..., gt=0, description="ID del viaje en el microservicio de Viajes")
    pasajero_id: int = Field(..., gt=0, description="ID del pasajero en el microservicio de Usuarios")
    pasajero_nombre: Optional[str] = Field(None, max_length=100, description="Nombre visible del pasajero")
    pasajero_correo: Optional[str] = Field(None, max_length=120, description="Correo institucional del pasajero")
    cupos_reservados: int = Field(default=1, gt=0, le=4, description="Cantidad de cupos a reservar en el viaje")
    punto_encuentro: Optional[str] = Field(
        None,
        max_length=150,
        description="Punto específico de recogida acordado dentro de la ruta"
    )
    comentarios: Optional[str] = Field(
        None,
        max_length=255,
        description="Notas o comentarios adicionales para el conductor"
    )

class ReservaCreate(ReservaBase):
    """Datos requeridos para crear una nueva reserva."""
    pass

class ReservaUpdate(BaseModel):
    """Campos editables de una reserva activa."""
    punto_encuentro: Optional[str] = Field(None, max_length=150, description="Nuevo punto de recogida")
    comentarios: Optional[str] = Field(None, max_length=255, description="Comentarios actualizados")

class ReservaEstadoUpdate(BaseModel):
    """Permite cambiar el estado de una reserva (por ejemplo, a COMPLETADA o CANCELADA)."""
    estado: Literal["CONFIRMADA", "CANCELADA", "COMPLETADA"] = Field(
        ...,
        description="Nuevo estado de la reserva"
    )

class ReservaResponse(ReservaBase):
    """Respuesta estándar con la información almacenada de la reserva."""
    id: int
    aporte_acordado: float
    origen_viaje: Optional[str] = None
    destino_viaje: Optional[str] = None
    fecha_hora_salida: Optional[datetime] = None
    conductor_nombre: Optional[str] = None
    estado: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReservaDetalladaResponse(BaseModel):
    """
    Respuesta enriquecida que combina los datos locales de la reserva
    con el estado en tiempo real del Microservicio de Viajes.
    Si el MS de Viajes está caído, activa `modo_degradado = True` y usa el snapshot local.
    """
    reserva: ReservaResponse
    viaje_en_vivo: Optional[dict] = Field(
        None,
        description="Datos actuales obtenidos del Microservicio de Viajes (si está disponible)"
    )
    modo_degradado: bool = Field(
        default=False,
        description="True si el MS de Viajes no respondió y se sirvió información desde el caché local"
    )
    aviso_sistema: Optional[str] = None

class MensajeResponse(BaseModel):
    mensaje: str
    detalles: Optional[dict] = None
