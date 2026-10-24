from datetime import datetime

from app.database import coneccion_database
from app.database.coneccion_database import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime


class mapeo_comunicacion_tabla(coneccion_database.Base):
    __tablename__ = "usuarios"  
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(120), nullable=False)
    correo_institucional = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    tipo_usuario = Column(String(20), nullable=False)
    telefono = Column(String(20), nullable=False)
    es_conductor = Column(Boolean, nullable=False, default=False)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.now)