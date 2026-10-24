import os
from pathlib import Path

# Cargar variables desde .env si existe de manera directa y ligera
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

class Settings:
    PROJECT_NAME: str = "UNIRIDE - Microservicio de Reservas"
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "uniride-reservas-service")
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:1234@localhost:5432/uniride_reservas_db"
    )
    PORT: int = int(os.getenv("PORT", "8003"))
    VIAJES_SERVICE_URL: str = os.getenv("VIAJES_SERVICE_URL", "http://localhost:8002").rstrip("/")
    USUARIOS_SERVICE_URL: str = os.getenv("USUARIOS_SERVICE_URL", "http://localhost:8001").rstrip("/")
    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "5.0"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
