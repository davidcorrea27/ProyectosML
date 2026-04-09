
# Configuración de conexión a la base de datos
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
#  Conectar FastAPI con PostgreSQL
# Formato: postgresql://usuario:password@host:puerto/nombre_db
# Cambia usuario, password y nombre_db según configuración en pgAdmin
 
# El motor de conexión: sabe cómo hablar con PostgreSQL
#engine = create_engine(DATABASE_URL)
 
# Lee DATABASE_URL desde variable de entorno
# En local usa tu DB de PostgreSQL como valor por defecto
# En Render usará la URL que configures en las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL") 
# El motor de conexión: sabe cómo hablar con PostgreSQL
engine = create_engine(DATABASE_URL)







# Fábrica de sesiones: cada petición abrirá una sesión nueva
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Clase base de la que heredarán todos los modelos de tabla
Base = declarative_base()
 
 
# TDependency Injection
# Función que abre y cierra la sesión por cada petición
# FastAPI la inyecta automáticamente con Depends(get_db)
def get_db():
    db = SessionLocal()
    try:
        yield db       # entrega la sesión al endpoint
    finally:
        db.close()     # siempre se cierra aunque haya error