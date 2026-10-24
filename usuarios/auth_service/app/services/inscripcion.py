from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.database.coneccion_database import Session
from app.models.mapeo_sql_tabla import mapeo_comunicacion_tabla

TIPOS_VALIDOS = ["estudiante", "profesor", "administrativo"]

def validacion_datos_inscripcion(validar_contraseña):
    if len(validar_contraseña) >= 8:
        return True
    return False

def verificacion_si_se_repite(correo):
    conexion = Session()
    usuarios = conexion.query(mapeo_comunicacion_tabla).filter_by(
        correo_institucional=correo
    ).first()
    conexion.close()
    return usuarios

def ejecutar_inscripcion_servicio(nombre, correo, password, telefono, tipo_usuario):
    if tipo_usuario.lower() not in TIPOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Tipo de usuario no válido. Debe ser estudiante, profesor o administrativo.")

    if verificacion_si_se_repite(correo):
        raise HTTPException(status_code=400, detail="El correo ya está registrado. Por favor, ingrese un correo diferente.")

    if not validacion_datos_inscripcion(password):
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")

    conexion = Session()
    usuario = mapeo_comunicacion_tabla(
        nombre_completo=nombre,
        correo_institucional=correo,
        password=password,
        telefono=telefono,
        tipo_usuario=tipo_usuario.lower()
    )
    conexion.add(usuario)
    try:
        conexion.commit()
        return {"mensaje": "¡Usuario registrado con éxito!", "correo": correo}
    except IntegrityError:
        conexion.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar el usuario. Por favor, inténtelo de nuevo.")
    finally:
        conexion.close()