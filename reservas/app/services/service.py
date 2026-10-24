from datetime import datetime
from typing import Optional, List
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Reserva
from app.schemas.schemas import (
    ReservaCreate,
    ReservaUpdate,
    ReservaResponse,
    ReservaDetalladaResponse
)

# =====================================================================
# Excepciones de Dominio y Sistemas Distribuidos
# =====================================================================

class ServicioViajesNoDisponibleError(Exception):
    """Se lanza cuando el Microservicio de Viajes no responde o rechaza la conexión."""
    pass

class RecursoNoEncontradoError(KeyError):
    """Se lanza cuando el viaje o la reserva solicitada no existe."""
    pass

class ConflictoReservaError(ValueError):
    """Se lanza cuando existe una regla de negocio o conflicto que impide la reserva."""
    pass


# =====================================================================
# Clientes HTTP para Comunicación Inter-Microservicios
# =====================================================================

def verificar_estado_ms_viajes() -> dict:
    """
    Consulta el healthcheck del Microservicio de Viajes para monitoreo distribuido.
    No lanza excepción si falla; retorna el estado de conectividad.
    """
    url = f"{settings.VIAJES_SERVICE_URL}/health"
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                return {"conectado": True, "url": settings.VIAJES_SERVICE_URL, "detalle": response.json()}
            return {"conectado": False, "url": settings.VIAJES_SERVICE_URL, "codigo_http": response.status_code}
    except httpx.HTTPError as exc:
        return {"conectado": False, "url": settings.VIAJES_SERVICE_URL, "error": str(exc)}


def obtener_viaje_remoto(viaje_id: int) -> dict:
    """
    Obtiene la información actual de un viaje consultando por HTTP al Microservicio de Viajes.
    """
    url = f"{settings.VIAJES_SERVICE_URL}/viajes/{viaje_id}"
    try:
        with httpx.Client(timeout=settings.HTTP_TIMEOUT) as client:
            response = client.get(url)
    except (httpx.RequestError, httpx.TimeoutException) as exc:
        raise ServicioViajesNoDisponibleError(
            f"No fue posible comunicarse con el Microservicio de Viajes ({settings.VIAJES_SERVICE_URL}). "
            f"Detalle técnico: {exc}"
        )

    if response.status_code == 404:
        raise RecursoNoEncontradoError(f"El viaje con ID {viaje_id} no existe en el Microservicio de Viajes.")

    if response.status_code != 200:
        detalle = response.json().get("detail", response.text) if response.content else "Error desconocido"
        raise ServicioViajesNoDisponibleError(
            f"El Microservicio de Viajes respondió con un estado inesperado ({response.status_code}): {detalle}"
        )

    return response.json()


def modificar_cupos_remoto(viaje_id: int, delta_cupos: int) -> dict:
    """
    Solicita al Microservicio de Viajes descontar (delta < 0) o restaurar (delta > 0)
    los cupos disponibles de un viaje mediante PATCH /viajes/{id}/cupos.
    """
    url = f"{settings.VIAJES_SERVICE_URL}/viajes/{viaje_id}/cupos"
    try:
        with httpx.Client(timeout=settings.HTTP_TIMEOUT) as client:
            response = client.patch(url, json={"delta_cupos": delta_cupos})
    except (httpx.RequestError, httpx.TimeoutException) as exc:
        raise ServicioViajesNoDisponibleError(
            f"Fallo de red al intentar actualizar los cupos en el Microservicio de Viajes: {exc}"
        )

    if response.status_code == 404:
        raise RecursoNoEncontradoError(f"El viaje con ID {viaje_id} no fue encontrado al actualizar cupos.")

    if response.status_code == 400:
        detalle = response.json().get("detail", "No fue posible modificar los cupos del viaje.")
        raise ValueError(detalle)

    if response.status_code != 200:
        raise ServicioViajesNoDisponibleError(
            f"Error del Microservicio de Viajes al actualizar cupos (HTTP {response.status_code})."
        )

    return response.json()


def obtener_nombre_usuario_remoto(pasajero_id: int) -> Optional[str]:
    """
    Intenta consultar opcionalmente el nombre del pasajero en el Microservicio de Usuarios.
    Si el servicio de Usuarios está apagado (tolerancia a fallos), retorna None sin interrumpir la reserva.
    """
    url = f"{settings.USUARIOS_SERVICE_URL}/usuarios/{pasajero_id}"
    try:
        with httpx.Client(timeout=1.5) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("nombre") or data.get("nombre_completo")
    except httpx.HTTPError:
        pass
    return None


# =====================================================================
# Lógica de Negocio y Coordinación Distribuida (Patrón Saga)
# =====================================================================

def crear_reserva(db: Session, reserva_data: ReservaCreate) -> Reserva:
    """
    Crea una nueva reserva coordinando con el Microservicio de Viajes:
    1. Verifica que el pasajero no tenga ya una reserva activa en el mismo viaje.
    2. Valida en el MS de Viajes que el viaje exista, esté PROGRAMADO y tenga cupos suficientes.
    3. Descuenta en tiempo real los cupos en el MS de Viajes (PATCH /viajes/{id}/cupos).
    4. Registra la reserva en PostgreSQL junto con un snapshot de los datos del viaje.
    5. Si ocurre un fallo local de base de datos tras descontar el cupo, ejecuta una
       transacción compensatoria (Rollback distribuido) devolviendo el cupo al MS de Viajes.
    """
    # 1. Evitar reservas duplicadas activas del mismo pasajero en el mismo viaje
    reserva_existente = (
        db.query(Reserva)
        .filter(
            Reserva.viaje_id == reserva_data.viaje_id,
            Reserva.pasajero_id == reserva_data.pasajero_id,
            Reserva.estado == "CONFIRMADA"
        )
        .first()
    )
    if reserva_existente:
        raise ConflictoReservaError(
            f"El pasajero #{reserva_data.pasajero_id} ya tiene una reserva CONFIRMADA "
            f"(ID #{reserva_existente.id}) para el viaje #{reserva_data.viaje_id}."
        )

    # 2. Consultar y validar el viaje en el Microservicio de Viajes
    viaje_info = obtener_viaje_remoto(reserva_data.viaje_id)

    if viaje_info.get("estado") != "PROGRAMADO":
        raise ValueError(
            f"No es posible reservar en el viaje #{reserva_data.viaje_id} porque su estado actual es '{viaje_info.get('estado')}'."
        )

    if viaje_info.get("conductor_id") == reserva_data.pasajero_id:
        raise ConflictoReservaError(
            "El conductor del viaje no puede realizar una reserva como pasajero en su propio viaje."
        )

    cupos_disponibles = viaje_info.get("cupos_disponibles", 0)
    if cupos_disponibles < reserva_data.cupos_reservados:
        raise ValueError(
            f"Cupos insuficientes en el viaje #{reserva_data.viaje_id}. "
            f"Solicitados: {reserva_data.cupos_reservados}, Disponibles: {cupos_disponibles}."
        )

    # Resolver nombre del pasajero (usa el enviado, o intenta MS Usuarios, o asigna genérico)
    nombre_pasajero = reserva_data.pasajero_nombre
    if not nombre_pasajero:
        nombre_pasajero = obtener_nombre_usuario_remoto(reserva_data.pasajero_id) or f"Pasajero #{reserva_data.pasajero_id}"

    # 3. Descontar cupo(s) en tiempo real en el Microservicio de Viajes
    modificar_cupos_remoto(reserva_data.viaje_id, delta_cupos=-reserva_data.cupos_reservados)

    # Parsear fecha_hora_salida del snapshot del viaje
    fecha_salida_raw = viaje_info.get("fecha_hora_salida")
    fecha_salida_dt = None
    if isinstance(fecha_salida_raw, str):
        try:
            fecha_salida_dt = datetime.fromisoformat(fecha_salida_raw.replace("Z", "+00:00"))
        except ValueError:
            fecha_salida_dt = None

    aporte_unitario = float(viaje_info.get("aporte_sugerido", 0.0))
    aporte_total = aporte_unitario * reserva_data.cupos_reservados

    # 4. Guardar la reserva en la base de datos local (con compensación Saga si falla)
    try:
        nueva_reserva = Reserva(
            viaje_id=reserva_data.viaje_id,
            pasajero_id=reserva_data.pasajero_id,
            pasajero_nombre=nombre_pasajero,
            pasajero_correo=reserva_data.pasajero_correo,
            cupos_reservados=reserva_data.cupos_reservados,
            punto_encuentro=reserva_data.punto_encuentro or viaje_info.get("origen"),
            comentarios=reserva_data.comentarios,
            aporte_acordado=aporte_total,
            origen_viaje=viaje_info.get("origen"),
            destino_viaje=viaje_info.get("destino"),
            fecha_hora_salida=fecha_salida_dt,
            conductor_nombre=viaje_info.get("conductor_nombre"),
            estado="CONFIRMADA"
        )
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
        return nueva_reserva
    except Exception as db_exc:
        db.rollback()
        # 5. COMPENSACIÓN SAGA: Revertir el descuento de cupos en el MS de Viajes
        try:
            modificar_cupos_remoto(reserva_data.viaje_id, delta_cupos=reserva_data.cupos_reservados)
        except Exception:
            pass
        raise RuntimeError(f"Error al persistir la reserva localmente (cupos restaurados en Viajes): {db_exc}")


def listar_reservas(
    db: Session,
    viaje_id: Optional[int] = None,
    pasajero_id: Optional[int] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Reserva]:
    """
    Lista las reservas registradas permitiendo filtrar por viaje, pasajero y estado.
    Funciona de manera 100% autónoma desde la base de datos de Reservas,
    incluso si el Microservicio de Viajes está fuera de línea.
    """
    query = db.query(Reserva)

    if viaje_id is not None:
        query = query.filter(Reserva.viaje_id == viaje_id)

    if pasajero_id is not None:
        query = query.filter(Reserva.pasajero_id == pasajero_id)

    if estado:
        query = query.filter(Reserva.estado == estado.upper())

    return query.order_by(Reserva.created_at.desc()).offset(skip).limit(limit).all()


def obtener_reserva_por_id(db: Session, reserva_id: int) -> Optional[Reserva]:
    """Obtiene una reserva específica por su ID."""
    return db.query(Reserva).filter(Reserva.id == reserva_id).first()


def obtener_reserva_detallada(db: Session, reserva_id: int) -> ReservaDetalladaResponse:
    """
    Obtiene una reserva y la enriquece en tiempo real con la información del Microservicio de Viajes.
    Demuestra Tolerancia a Fallos (Degradación Elegante): si el MS de Viajes está caído,
    retorna los datos locales del snapshot con `modo_degradado=True`.
    """
    reserva = obtener_reserva_por_id(db, reserva_id)
    if not reserva:
        raise RecursoNoEncontradoError(f"La reserva con ID {reserva_id} no fue encontrada.")

    reserva_schema = ReservaResponse.model_validate(reserva)

    try:
        viaje_en_vivo = obtener_viaje_remoto(reserva.viaje_id)
        return ReservaDetalladaResponse(
            reserva=reserva_schema,
            viaje_en_vivo=viaje_en_vivo,
            modo_degradado=False,
            aviso_sistema="Datos sincronizados en tiempo real con el Microservicio de Viajes."
        )
    except (ServicioViajesNoDisponibleError, RecursoNoEncontradoError) as exc:
        return ReservaDetalladaResponse(
            reserva=reserva_schema,
            viaje_en_vivo=None,
            modo_degradado=True,
            aviso_sistema=(
                "MODO DEGRADADO ACTIVO: El Microservicio de Viajes no está disponible en este momento. "
                f"Mostrando información de respaldo almacenada en la reserva. ({exc})"
            )
        )


def actualizar_reserva(
    db: Session,
    reserva_id: int,
    reserva_data: ReservaUpdate
) -> Optional[Reserva]:
    """Actualiza el punto de encuentro o los comentarios de una reserva existente."""
    reserva = obtener_reserva_por_id(db, reserva_id)
    if not reserva:
        return None

    if reserva.estado != "CONFIRMADA":
        raise ValueError(f"No se pueden modificar los detalles de una reserva en estado {reserva.estado}.")

    update_dict = reserva_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(reserva, key, value)

    db.commit()
    db.refresh(reserva)
    return reserva


def completar_reserva(db: Session, reserva_id: int) -> Reserva:
    """Marca una reserva CONFIRMADA como COMPLETADA una vez finalizado el trayecto."""
    reserva = obtener_reserva_por_id(db, reserva_id)
    if not reserva:
        raise RecursoNoEncontradoError(f"La reserva con ID {reserva_id} no fue encontrada.")

    if reserva.estado == "CANCELADA":
        raise ValueError("No se puede marcar como completada una reserva que fue cancelada.")

    if reserva.estado == "COMPLETADA":
        return reserva

    reserva.estado = "COMPLETADA"
    db.commit()
    db.refresh(reserva)
    return reserva


def cancelar_reserva(db: Session, reserva_id: int) -> Reserva:
    """
    Cancela una reserva activa y se comunica con el Microservicio de Viajes
    para restaurar los cupos que habían sido tomados (delta = +cupos_reservados).
    """
    reserva = obtener_reserva_por_id(db, reserva_id)
    if not reserva:
        raise RecursoNoEncontradoError(f"La reserva con ID {reserva_id} no fue encontrada.")

    if reserva.estado == "CANCELADA":
        raise ValueError(f"La reserva con ID {reserva_id} ya se encuentra CANCELADA.")

    if reserva.estado == "COMPLETADA":
        raise ValueError("No se puede cancelar una reserva cuyo viaje ya fue COMPLETADO.")

    # Liberar los cupos en el Microservicio de Viajes
    try:
        modificar_cupos_remoto(reserva.viaje_id, delta_cupos=reserva.cupos_reservados)
    except ValueError as ve:
        # Si el viaje ya había sido cancelado o cerrado por el conductor en el MS de Viajes,
        # permitimos que la reserva pase a estado CANCELADA localmente sin bloquear al usuario.
        if "estado CANCELADO" not in str(ve) and "capacidad total" not in str(ve):
            raise

    reserva.estado = "CANCELADA"
    db.commit()
    db.refresh(reserva)
    return reserva
