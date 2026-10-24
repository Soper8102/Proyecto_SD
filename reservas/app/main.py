from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.routes import router as reservas_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas en PostgreSQL si no existen al iniciar el microservicio
    print(f"[*] Iniciando {settings.PROJECT_NAME}...")
    Base.metadata.create_all(bind=engine)
    print("[*] Tablas de PostgreSQL sincronizadas en uniride_reservas_db.")
    yield
    print("[*] Deteniendo microservicio de Reservas...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Microservicio de gestión de reservas y control de cupos distribuidos para UNIRIDE.",
    lifespan=lifespan
)

# Habilitar CORS para permitir comunicación fluida con el API Gateway y el Frontend (React/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de reservas
app.include_router(reservas_router)

@app.get("/info", tags=["Monitoreo"])
def get_service_info():
    return {
        "microservicio": settings.PROJECT_NAME,
        "servicio_id": settings.SERVICE_NAME,
        "puerto": settings.PORT,
        "entorno": settings.ENVIRONMENT,
        "viajes_service_url": settings.VIAJES_SERVICE_URL,
        "estado": "En ejecución"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
