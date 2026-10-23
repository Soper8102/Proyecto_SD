# Microservicio de Usuarios y Autenticación (UNIRIDE)

Este microservicio se encarga del registro de usuarios (estudiantes y profesores), gestión de perfiles, inicio de sesión y registro de vehículos para conductores.

## Estructura del Código
* `app/models/models.py`: Modelos de base de datos en PostgreSQL (`Usuario`, `Vehiculo`).
* `app/schemas/schemas.py`: Validaciones de entrada y salida con Pydantic.
* `app/services/service.py`: Lógica de negocio (aquí puedes personalizar el hashing de contraseñas con bcrypt o JWT).
* `app/api/routes.py`: Endpoints REST (`/usuarios`, `/login`, `/{id}/vehiculos`).

## Cómo ejecutarlo localmente

1. Activa tu entorno virtual:
```powershell
.\venv\Scripts\activate
```

2. Instala las dependencias:
```powershell
pip install -r requirements.txt
```

3. Inicia el servidor (puerto 8001):
```powershell
uvicorn app.main:app --port 8001 --reload
```

Documentación interactiva disponible en: `http://localhost:8001/docs`

## Ejecución con Docker
```powershell
docker compose up --build -d
```
