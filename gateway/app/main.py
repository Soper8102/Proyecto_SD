from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="UNIRIDE API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#URLs locales por cada microservicio

USERS_SERVICE_URL = "http://localhost:8001"
TRIPS_SERVICE_URL = "http://localhost:8002"
BOOKINGS_SERVICE_URL = "http://localhost:8003"

@app.get("/")
def gateway_root():
    return {"mensaje": "API Gateway de UNIRIDE Activo y Operativo"}

@app.get("/usuarios")
async def proxy_get_usuarios():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USERS_SERVICE_URL}/")
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="El servicio de usuarios no está disponible.")

@app.get("/viajes")
async def proxy_get_viajes():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{TRIPS_SERVICE_URL}/")
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="El servicio de viajes no está activo.")

@app.post("/reservas")
async def proxy_crear_reserva(payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BOOKINGS_SERVICE_URL}/reservas", json=payload, timeout=3.0)
            return response.json()
        except (httpx.RequestError, httpx.TimeoutException):
            raise HTTPException(
                status_code=503,
                detail="El servicio de reservas no está disponible. Puede consultar los viajes, pero no realizar una reserva."
            )