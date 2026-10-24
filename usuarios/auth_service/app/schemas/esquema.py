from pydantic import BaseModel, EmailStr

class UsuarioRegistro(BaseModel):
    nombre_completo: str
    correo_institucional: str
    password: str
    telefono: str
    tipo_usuario: str