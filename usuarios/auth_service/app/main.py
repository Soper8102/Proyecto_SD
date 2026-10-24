from fastapi import FastAPI
import uvicorn
from app.routes.auth_routes import router as auth_router

app = FastAPI(
    title="Auth Service",
    description="Microservicio de autenticación y gestión de usuarios",
    version="1.0.0"
)

# Registras el router en la aplicación principal
app.include_router(auth_router)

@app.get("/")
def home():
    return {"mensaje": "¡Bienvenido al microservicio de Autenticación (Auth-Service)!"}

if __name__ == "__main__":
    # Importante: Debe ser "app.main:app" para que Uvicorn encuentre el módulo correctamente
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)