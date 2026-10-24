from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import (
    ReservaCreate,
    ReservaUpdate,
    ReservaResponse,
    ReservaDetalladaResponse,
    MensajeResponse
)
from app.services import service
from app.services.service import (
    ServicioViajesNoDisponibleError,
    RecursoNoEncontradoError,
    ConflictoReservaError
)

router = APIRouter(tags=["Reservas"])

@router.get(
    "/health",
    summary="Health check del microservicio de reservas y conectividad con Viajes",
    response_model=dict
)
def health_check():
    estado_viajes = service.verificar_estado_ms_viajes()
    return {
        "servicio": "Microservicio de Reservas",
        "estado": "OPERATIVO",
        "version": "1.0.0",
        "dependencias": {
            "ms_viajes": estado_viajes
        }
    }

@router.get(
    "/",
    response_model=List[ReservaResponse],
    summary="Listar todas las reservas con filtros opcionales"
)
@router.get(
    "/reservas",
    response_model=List[ReservaResponse],
    include_in_schema=False
)
def get_reservas(
    viaje_id: Optional[int] = Query(None, description="Filtrar por ID del viaje"),
    pasajero_id: Optional[int] = Query(None, description="Filtrar por ID del pasajero"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: CONFIRMADA, CANCELADA o COMPLETADA"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retorna la lista de reservas registradas en PostgreSQL.
    Permite filtrar por viaje, pasajero y estado de la reserva.
    """
    return service.listar_reservas(
        db=db,
        viaje_id=viaje_id,
        pasajero_id=pasajero_id,
        estado=estado,
        skip=skip,
        limit=limit
    )

@router.post(
    "/",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva reserva y descontar cupos en el MS de Viajes"
)
@router.post(
    "/reservas",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_reserva(
    reserva_in: ReservaCreate,
    db: Session = Depends(get_db)
):
    """
    Registra una nueva reserva para un pasajero en un viaje programado.
    Se comunica sincrónicamente con el Microservicio de Viajes para validar disponibilidad
    y descontar los cupos en tiempo real.
    """
    try:
        return service.crear_reserva(db=db, reserva_data=reserva_in)
    except ServicioViajesNoDisponibleError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except RecursoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictoReservaError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/pasajero/{pasajero_id}",
    response_model=List[ReservaResponse],
    summary="Consultar el historial de reservas de un pasajero"
)
@router.get(
    "/reservas/pasajero/{pasajero_id}",
    response_model=List[ReservaResponse],
    include_in_schema=False
)
def get_reservas_por_pasajero(
    pasajero_id: int,
    estado: Optional[str] = Query(None, description="Filtrar por estado opcional"),
    db: Session = Depends(get_db)
):
    """Retorna todas las reservas asociadas a un pasajero específico."""
    return service.listar_reservas(db=db, pasajero_id=pasajero_id, estado=estado)

@router.get(
    "/viaje/{viaje_id}",
    response_model=List[ReservaResponse],
    summary="Consultar los pasajeros/reservas de un viaje específico"
)
@router.get(
    "/reservas/viaje/{viaje_id}",
    response_model=List[ReservaResponse],
    include_in_schema=False
)
def get_reservas_por_viaje(
    viaje_id: int,
    estado: Optional[str] = Query("CONFIRMADA", description="Filtrar por estado (por defecto CONFIRMADA)"),
    db: Session = Depends(get_db)
):
    """Retorna las reservas realizadas para un viaje determinado (útil para el conductor)."""
    return service.listar_reservas(db=db, viaje_id=viaje_id, estado=estado)

@router.get(
    "/{reserva_id}",
    response_model=ReservaResponse,
    summary="Consultar una reserva por su ID"
)
@router.get(
    "/reservas/{reserva_id}",
    response_model=ReservaResponse,
    include_in_schema=False
)
def get_reserva_by_id(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    reserva = service.obtener_reserva_por_id(db=db, reserva_id=reserva_id)
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La reserva con ID {reserva_id} no fue encontrada."
        )
    return reserva

@router.get(
    "/{reserva_id}/detalle",
    response_model=ReservaDetalladaResponse,
    summary="Consultar reserva enriquecida con datos en vivo del MS de Viajes (Soporta Modo Degradado)"
)
@router.get(
    "/reservas/{reserva_id}/detalle",
    response_model=ReservaDetalladaResponse,
    include_in_schema=False
)
def get_reserva_detallada(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Combina la información local de la reserva con el estado en tiempo real del viaje.
    Si el Microservicio de Viajes está caído, responde en Modo Degradado usando el snapshot local.
    """
    try:
        return service.obtener_reserva_detallada(db=db, reserva_id=reserva_id)
    except RecursoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put(
    "/{reserva_id}",
    response_model=ReservaResponse,
    summary="Actualizar punto de encuentro o comentarios de una reserva"
)
@router.put(
    "/reservas/{reserva_id}",
    response_model=ReservaResponse,
    include_in_schema=False
)
def update_reserva(
    reserva_id: int,
    reserva_in: ReservaUpdate,
    db: Session = Depends(get_db)
):
    try:
        reserva_actualizada = service.actualizar_reserva(
            db=db,
            reserva_id=reserva_id,
            reserva_data=reserva_in
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not reserva_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La reserva con ID {reserva_id} no fue encontrada para actualizar."
        )
    return reserva_actualizada

@router.patch(
    "/{reserva_id}/completar",
    response_model=ReservaResponse,
    summary="Marcar una reserva como COMPLETADA al finalizar el viaje"
)
@router.patch(
    "/reservas/{reserva_id}/completar",
    response_model=ReservaResponse,
    include_in_schema=False
)
def complete_reserva(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    try:
        return service.completar_reserva(db=db, reserva_id=reserva_id)
    except RecursoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete(
    "/{reserva_id}",
    response_model=MensajeResponse,
    summary="Cancelar una reserva y liberar sus cupos en el MS de Viajes"
)
@router.delete(
    "/reservas/{reserva_id}",
    response_model=MensajeResponse,
    include_in_schema=False
)
def cancel_reserva(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancela una reserva activa y se comunica con el Microservicio de Viajes
    para devolver los cupos reservados (delta = +cupos_reservados).
    """
    try:
        reserva = service.cancelar_reserva(db=db, reserva_id=reserva_id)
        return MensajeResponse(
            mensaje=f"La reserva con ID {reserva_id} ha sido cancelada exitosamente y se liberaron {reserva.cupos_reservados} cupo(s) en el viaje #{reserva.viaje_id}.",
            detalles={
                "reserva_id": reserva.id,
                "viaje_id": reserva.viaje_id,
                "cupos_liberados": reserva.cupos_reservados,
                "nuevo_estado": reserva.estado
            }
        )
    except ServicioViajesNoDisponibleError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except RecursoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
