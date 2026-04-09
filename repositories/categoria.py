# repositories/categoria.py 
#  Category Repository

 
from fastapi import HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from models import Categoria, Prediccion
 
 
class CategoriaRepository:
 
    # Obtener categoría por ID
    def obtener_por_id(self, db: Session, categoria_id: int) -> Categoria:
        cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return cat
 
    # Devuelve query sin ejecutar para que el servicio pagine
    def listar_query(self, db: Session, busqueda: str = None):
        query = db.query(Categoria)
        if busqueda:
            query = query.filter(Categoria.nombre.ilike(f"%{busqueda}%"))
        return query.order_by(Categoria.nombre)
 
    # Ensure: garantiza que la categoría existe antes de usarla
    def ensure_categoria(self, db: Session, categoria_id: int) -> Categoria:
        return self.obtener_por_id(db, categoria_id)
 
    # Crear categoría con normalización del nombre
    def crear(self, db: Session, nombre: str, descripcion: str = None) -> Categoria:
        nombre = nombre.lower().strip()
        existe = db.query(Categoria).filter(Categoria.nombre == nombre).first()
        if existe:
            raise HTTPException(status_code=400, detail="La categoría ya existe")
        nueva = Categoria(nombre=nombre, descripcion=descripcion)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva
 
    # Actualizar nombre y/o descripción
    def actualizar(self, db: Session, categoria_id: int, nombre: str = None, descripcion: str = None) -> Categoria:
        cat = self.obtener_por_id(db, categoria_id)
        if nombre is not None:
            cat.nombre = nombre.lower().strip()
        if descripcion is not None:
            cat.descripcion = descripcion
        db.commit()
        db.refresh(cat)
        return cat
 
    # Eliminar categoría
    def eliminar(self, db: Session, categoria_id: int) -> dict:
        cat = self.obtener_por_id(db, categoria_id)
        db.delete(cat)
        db.commit()
        return {"mensaje": f"Categoría '{cat.nombre}' eliminada"}
 
    # Categoría más popular — la que más predicciones tiene
    def mas_popular(self, db: Session) -> dict:
        resultado = (
            db.query(
                Categoria,
                func.count(Prediccion.id).label("total")
            )
            .join(Prediccion, Categoria.id == Prediccion.categoria_id)
            .group_by(Categoria.id)
            .order_by(desc("total"))
            .first()
        )
        if not resultado:
            raise HTTPException(
                status_code=404,
                detail="No hay categorías asociadas a predicciones"
            )
        cat, total = resultado
        return {
            "id":                 cat.id,
            "nombre":             cat.nombre,
            "descripcion":        cat.descripcion,
            "total_predicciones": total
        }
 
 
# Instancia única compartida
categoria_repo = CategoriaRepository()