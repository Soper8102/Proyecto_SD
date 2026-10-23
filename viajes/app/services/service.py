from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.models import Viaje
from app.schemas.schemas import ViajeCreate, ViajeUpdate

def crear_viaje(db: Session, viaje_data: ViajeCreate) -> Viaje:
    """
    Crea un nuevo viaje en la base de datos.
    Inicializa los cupos disponibles iguales a los cupos totales.
    """
    # Validar coherencia según tipo de vehículo
    if viaje_data.tipo_vehiculo == "moto" and viaje_data.cupos_totales > 1:
        raise ValueError("Una moto solo puede ofrecer un máximo de 1 cupo para pasajero.")

    nuevo_viaje = Viaje(
        conductor_id=viaje_data.conductor_id,
        conductor_nombre=viaje_data.conductor_nombre or f"Conductor #{viaje_data.conductor_id}",
        origen=viaje_data.origen,
        destino=viaje_data.destino,
        fecha_hora_salida=viaje_data.fecha_hora_salida,
        descripcion_ruta=viaje_data.descripcion_ruta,
        cupos_totales=viaje_data.cupos_totales,
        cupos_disponibles=viaje_data.cupos_totales, # Inicialmente todos disponibles
        aporte_sugerido=viaje_data.aporte_sugerido,
        tipo_vehiculo=viaje_data.tipo_vehiculo,
        placa_vehiculo=viaje_data.placa_vehiculo,
        estado="PROGRAMADO"
    )
    db.add(nuevo_viaje)
    db.commit()
    db.refresh(nuevo_viaje)
    return nuevo_viaje

def listar_viajes(
    db: Session,
    origen: Optional[str] = None,
    destino: Optional[str] = None,
    tipo_vehiculo: Optional[str] = None,
    solo_disponibles: bool = True,
    conductor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Viaje]:
    """
    Consulta viajes con filtros opcionales de búsqueda.
    """
    query = db.query(Viaje)

    if solo_disponibles:
        query = query.filter(Viaje.cupos_disponibles > 0, Viaje.estado == "PROGRAMADO")

    if origen:
        query = query.filter(Viaje.origen.ilike(f"%{origen}%"))

    if destino:
        query = query.filter(Viaje.destino.ilike(f"%{destino}%"))

    if tipo_vehiculo:
        query = query.filter(Viaje.tipo_vehiculo == tipo_vehiculo.lower())

    if conductor_id:
        query = query.filter(Viaje.conductor_id == conductor_id)

    return query.order_by(Viaje.fecha_hora_salida.asc()).offset(skip).limit(limit).all()

def obtener_viaje_por_id(db: Session, viaje_id: int) -> Optional[Viaje]:
    """Obtiene un viaje específico por su ID."""
    return db.query(Viaje).filter(Viaje.id == viaje_id).first()

def actualizar_viaje(db: Session, viaje_id: int, viaje_data: ViajeUpdate) -> Optional[Viaje]:
    """Actualiza campos específicos de un viaje existente."""
    viaje = obtener_viaje_por_id(db, viaje_id)
    if not viaje:
        return None

    update_dict = viaje_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(viaje, key, value)

    db.commit()
    db.refresh(viaje)
    return viaje

def modificar_cupos_disponibles(db: Session, viaje_id: int, delta: int) -> Viaje:
    """
    Modifica los cupos disponibles de un viaje.
    Delta negativo resta cupos (reserva realizada).
    Delta positivo suma cupos (reserva cancelada o rechazada).
    Lanza ValueError si no hay cupos o si supera la capacidad total.
    """
    viaje = obtener_viaje_por_id(db, viaje_id)
    if not viaje:
        raise KeyError(f"El viaje con ID {viaje_id} no fue encontrado.")

    if viaje.estado != "PROGRAMADO":
        raise ValueError(f"No se pueden modificar cupos de un viaje en estado {viaje.estado}.")

    nuevo_cupo = viaje.cupos_disponibles + delta

    if nuevo_cupo < 0:
        raise ValueError("No hay cupos disponibles suficientes en este viaje.")

    if nuevo_cupo > viaje.cupos_totales:
        raise ValueError("Los cupos disponibles no pueden superar la capacidad total del viaje.")

    viaje.cupos_disponibles = nuevo_cupo
    db.commit()
    db.refresh(viaje)
    return viaje

def cancelar_viaje(db: Session, viaje_id: int) -> Optional[Viaje]:
    """Marca un viaje como cancelado."""
    viaje = obtener_viaje_por_id(db, viaje_id)
    if not viaje:
        return None

    viaje.estado = "CANCELADO"
    viaje.cupos_disponibles = 0
    db.commit()
    db.refresh(viaje)
    return viaje
