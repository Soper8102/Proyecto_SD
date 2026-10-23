# pyrefly: ignore [missing-import]
from starlette.status import status
from fastapi import responses
from httpx import _status_codes
from starlette.requests import http_cookies
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="UNIREDE API Gateway", version="1.0.0")

#URLs locales por cada microservicio

USERS_SERVICE_URL = "http://localhost:8001"
TRIPS_SERVICE_URL = "http://localhost:8002"
BOOKINGS_SERVICE_URL = "http:localhost:8003"

@app.get("/")
def gateway_root():
    return {"mensaje":"API Gateway de UNIRIDE Activo y Operativo"}

@app.get("/usuarios")
async def proxy_get_usuarios():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USERS_SERVICE_URL}/", )
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
            raise HTTPException(status_code=503, detail="El servicio de viajes no está activo")

@app.post("/reservas")
async def proxy_get_reservas():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BOOKINGS_SERVICE_URL}/", json=payload, timeout=3.0)
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="El servicio de reservas no está disponible :(. Puede consultar los viajes, pero no realizar una reserva. ")