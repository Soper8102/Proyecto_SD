# Microservicio de Reservas (UNIRIDE)

Este microservicio se encarga de crear reservas para los viajes, gestionar cancelaciones y comunicarse con el microservicio de Viajes para verificar y descontar cupos en tiempo real.

## Estructura del Código
* `app/models/models.py`: Modelo ORM `Reserva` en PostgreSQL.
* `app/schemas/schemas.py`: Validaciones de entrada y salida con Pydantic.
* `app/services/service.py`: Lógica de reserva, validación de cupos y llamadas HTTP al servicio de Viajes.
* `app/api/routes.py`: Endpoints REST (`POST /reservas`, `GET /reservas`, `DELETE /reservas/{id}`).

## Cómo ejecutarlo localmente

1. Activa tu entorno virtual:
```powershell
.\venv\Scripts\activate
```

2. Instala las dependencias:
```powershell
pip install -r requirements.txt
```

3. Inicia el servidor (puerto 8003):
```powershell
uvicorn app.main:app --port 8003 --reload
```

Documentación interactiva disponible en: `http://localhost:8003/docs`

## Ejecución con Docker
```powershell
docker compose up --build -d
```
