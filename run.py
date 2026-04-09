# run.py — 
# Archivo run seeds
#  Archivo de inicio y probando seeds
# Corre este archivo con python run.py
# Puebla la DB con datos iniciales sin ir a Swagger manualmente
import sys
import os
 
# asegura que Python encuentre los módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
from contextlib import contextmanager
from database import Base, engine, SessionLocal
from seeds import seed_usuarios, seed_categorias, seed_tags
 
 
# contextmanager — equivalente al Depends(get_db) de FastAPI
# pero para scripts que corren fuera del servidor
@contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()      # confirma todos los cambios al final
        print("Commit realizado correctamente")
    except Exception as e:
        db.rollback()    # revierte todo si algo falla
        print(f"Error en seed, rollback realizado: {e}")
        raise e
    finally:
        db.close()
 
 
def run_seeds():
    print("=" * 40)
    print("Iniciando seeds...")
    print("=" * 40)
 
    # crea las tablas si no existen
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas/creadas")
 
    # ejecuta todos los seeds en una sola sesión
    # el orden importa: usuarios primero porque predicciones los referencian
    with get_session() as db:
        seed_usuarios.run(db)
        seed_categorias.run(db)
        seed_tags.run(db)
 
    print("=" * 40)
    print("Seeds completados exitosamente")
    print("Puedes hacer login con:")
    print("  admin@iris.com     / admin123  (admin)")
    print("  cientifico@iris.com / user123  (user)")
    print("=" * 40)
 
 
if __name__ == "__main__":
    run_seeds()