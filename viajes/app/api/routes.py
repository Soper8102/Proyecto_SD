from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import (
    ViajeCreate,
    ViajeUpdate,
    ViajeResponse,
    ActualizarCuposRequest,
    MensajeResponse
)
from app.services import service

router = APIRouter(tags=["Viajes"])

@router.get(
    "/health",
    summary="Health check del microservicio de viajes",
    response_model=dict
)
def health_check():
    return {
        "servicio": "Microservicio de Viajes",
        "estado": "OPERATIVO",
        "version": "1.0.0"
    }

@router.get(
    "/",
    response_model=List[ViajeResponse],
    summary="Listar todos los viajes con filtros opcionales"
)
@router.get(
    "/viajes",
    response_model=List[ViajeResponse],
    include_in_schema=False
)
def get_viajes(
    origen: Optional[str] = Query(None, description="Filtrar por coincidencia en origen"),
    destino: Optional[str] = Query(None, description="Filtrar por coincidencia en destino"),
    tipo_vehiculo: Optional[str] = Query(None, description="carro o moto"),
    solo_disponibles: bool = Query(True, description="Mostrar únicamente viajes con cupos > 0"),
    conductor_id: Optional[int] = Query(None, description="Filtrar por conductor específico"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retorna la lista de viajes registrados.
    Permite filtrar por origen, destino, tipo de vehículo y disponibilidad.
    """
    return service.listar_viajes(
        db=db,
        origen=origen,
        destino=destino,
        tipo_vehiculo=tipo_vehiculo,
        solo_disponibles=solo_disponibles,
        conductor_id=conductor_id,
        skip=skip,
        limit=limit
    )

@router.post(
    "/",
    response_model=ViajeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo viaje"
)
@router.post(
    "/viajes",
    response_model=ViajeResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_viaje(
    viaje_in: ViajeCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo viaje programado por un conductor.
    """
    try:
        return service.crear_viaje(db=db, viaje_data=viaje_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/{viaje_id}",
    response_model=ViajeResponse,
    summary="Consultar un viaje por su ID"
)
@router.get(
    "/viajes/{viaje_id}",
    response_model=ViajeResponse,
    include_in_schema=False
)
def get_viaje_by_id(
    viaje_id: int,
    db: Session = Depends(get_db)
):
    viaje = service.obtener_viaje_por_id(db=db, viaje_id=viaje_id)
    if not viaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El viaje con ID {viaje_id} no fue encontrado."
        )
    return viaje

@router.put(
    "/{viaje_id}",
    response_model=ViajeResponse,
    summary="Actualizar información de un viaje"
)
@router.put(
    "/viajes/{viaje_id}",
    response_model=ViajeResponse,
    include_in_schema=False
)
def update_viaje(
    viaje_id: int,
    viaje_in: ViajeUpdate,
    db: Session = Depends(get_db)
):
    viaje_actualizado = service.actualizar_viaje(db=db, viaje_id=viaje_id, viaje_data=viaje_in)
    if not viaje_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El viaje con ID {viaje_id} no fue encontrado para actualizar."
        )
    return viaje_actualizado

@router.patch(
    "/{viaje_id}/cupos",
    response_model=ViajeResponse,
    summary="Modificar cupos disponibles (Consumido por el MS de Reservas)"
)
@router.patch(
    "/viajes/{viaje_id}/cupos",
    response_model=ViajeResponse,
    include_in_schema=False
)
def update_viaje_cupos(
    viaje_id: int,
    cupo_req: ActualizarCuposRequest,
    db: Session = Depends(get_db)
):
    """
    Permite al microservicio de Reservas descontar cupo (delta = -1)
    o restaurarlo en caso de cancelación (delta = +1).
    """
    try:
        return service.modificar_cupos_disponibles(db=db, viaje_id=viaje_id, delta=cupo_req.delta_cupos)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete(
    "/{viaje_id}",
    response_model=MensajeResponse,
    summary="Cancelar un viaje programado"
)
@router.delete(
    "/viajes/{viaje_id}",
    response_model=MensajeResponse,
    include_in_schema=False
)
def cancel_viaje(
    viaje_id: int,
    db: Session = Depends(get_db)
):
    viaje = service.cancelar_viaje(db=db, viaje_id=viaje_id)
    if not viaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El viaje con ID {viaje_id} no fue encontrado para cancelar."
        )
    return MensajeResponse(mensaje=f"El viaje con ID {viaje_id} ha sido cancelado exitosamente.")
