# Microservicio de Reservas (UNIRIDE)

Este microservicio gestiona el ciclo de vida completo de las reservas de cupos en los viajes de **UNIRIDE**, aplicando patrones de **Sistemas Distribuidos** como **Coordinación Saga con Compensación**, **Prevención de Doble Reserva (Idempotencia/Consistencia)** y **Degradación Elegante (Graceful Degradation)** mediante snapshots locales.

## Arquitectura y Estructura del Código
* `app/core/config.py`: Configuración centralizada mediante variables de entorno (`.env`).
* `app/core/database.py`: Conexión a PostgreSQL (`uniride_reservas_db`) con SQLAlchemy y `pool_pre_ping`.
* `app/models/models.py`: Modelo ORM `Reserva` con referencias lógicas (`viaje_id`, `pasajero_id`) y campos de snapshot del viaje (`origen_viaje`, `destino_viaje`, `fecha_hora_salida`, `conductor_nombre`).
* `app/schemas/schemas.py`: Esquemas Pydantic v2 para validación estricta de entrada y salida.
* `app/services/service.py`: Lógica de negocio y cliente HTTP (`httpx`) para comunicación síncrona con el Microservicio de Viajes (`PATCH /viajes/{id}/cupos`) y el Microservicio de Usuarios.
* `app/api/routes.py`: Endpoints REST completos:
  * `GET /health` y `GET /info`: Monitoreo del nodo y estado de conexión con el MS de Viajes.
  * `GET /reservas` (o `GET /`): Listado de reservas con filtros por `viaje_id`, `pasajero_id` y `estado`.
  * `POST /reservas` (o `POST /`): Creación de reserva validando disponibilidad y descontando cupos en tiempo real.
  * `GET /reservas/{id}`: Consulta de una reserva por ID.
  * `GET /reservas/{id}/detalle`: Consulta enriquecida con datos en vivo del MS de Viajes (o **Modo Degradado** automático si el MS de Viajes está apagado).
  * `GET /reservas/pasajero/{pasajero_id}`: Historial de reservas de un pasajero.
  * `GET /reservas/viaje/{viaje_id}`: Lista de pasajeros confirmados para un viaje.
  * `PUT /reservas/{id}`: Actualización de punto de encuentro o comentarios.
  * `PATCH /reservas/{id}/completar`: Marca una reserva como `COMPLETADA`.
  * `DELETE /reservas/{id}`: Cancela la reserva y restaura automáticamente los cupos en el MS de Viajes (`delta = +cupos_reservados`).
* `seed_data.py`: Script para poblar la base de datos con reservas de prueba de UNIMINUTO.
* `test_endpoints.py`: Pruebas automatizadas de todos los endpoints y escenarios de fallo distribuido.

## Cómo ejecutarlo localmente

1. Activa tu entorno virtual:
```powershell
.\venv\Scripts\activate
```

2. Instala las dependencias:
```powershell
pip install -r requirements.txt
```

3. (Opcional) Poblar datos de prueba:
```powershell
python seed_data.py
```

4. Inicia el servidor (puerto 8003):
```powershell
uvicorn app.main:app --port 8003 --reload
```

Documentación interactiva (Swagger UI) disponible en: `http://localhost:8003/docs`

## Ejecución con Docker
```powershell
docker compose up --build -d
```
