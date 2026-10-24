from fastapi import HTTPException
from app.database.coneccion_database import Session
from app.models.mapeo_sql_tabla import mapeo_comunicacion_tabla

def inicio_sesion_servicio(correo, contraseña):
    conexion = Session()
    usuario = conexion.query(mapeo_comunicacion_tabla).filter_by(
        correo_institucional=correo, 
        password=contraseña
    ).first()
    conexion.close()
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos.")
    
    return {"mensaje": "¡Inicio de sesión exitoso!", "correo": usuario.correo_institucional}