from app.database.coneccion_database import Base, engine
from app.models.mapeo_sql_tabla import mapeo_comunicacion_tabla

Base.metadata.create_all(engine)
print("Tablas creadas correctamente")