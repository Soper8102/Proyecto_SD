from fastapi import APIRouter
from pydantic import BaseModel
from app.services.inscripcion import ejecutar_inscripcion_servicio
from app.services.inicio_sesion import inicio_sesion_servicio

router = APIRouter()

class UsuarioRegistro(BaseModel):
    nombre_completo: str
    correo_institucional: str
    password: str
    telefono: str
    tipo_usuario: str

class UsuarioLogin(BaseModel):
    correo_institucional: str
    password: str

@router.post("/registro")
def registrar(datos: UsuarioRegistro):
    return ejecutar_inscripcion_servicio(
        nombre=datos.nombre_completo,
        correo=datos.correo_institucional,
        password=datos.password,
        telefono=datos.telefono,
        tipo_usuario=datos.tipo_usuario
    )

@router.post("/login")
def login(datos: UsuarioLogin):
    return inicio_sesion_servicio(
        correo=datos.correo_institucional,
        contraseña=datos.password
    )