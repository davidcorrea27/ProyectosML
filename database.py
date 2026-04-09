
# Configuración de conexión a la base de datos
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#  Conectar FastAPI con PostgreSQL
# Formato: postgresql://usuario:password@host:puerto/nombre_db
# Cambia usuario, password y nombre_db según configuración en pgAdmin
DATABASE_URL = "postgresql://postgres:termine6@localhost:5432/iris_db"
 
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