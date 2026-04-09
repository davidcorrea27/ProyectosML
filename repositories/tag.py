# repositories/tag.py — 
# Repository de tags
#  Update y Delete en repository
#  Tag más popular

from fastapi import HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from models import Tag, prediccion_tag
 
 
class TagRepository:
 
    #  Obtener tag por ID
    def obtener_por_id(self, db: Session, tag_id: int) -> Tag:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag no encontrado")
        return tag
 
    #  Listar tags con búsqueda opcional
    # Devuelve la QUERY sin ejecutar para que el servicio
    # de paginación la reciba y aplique offset/limit
    def listar_query(self, db: Session, busqueda: str = None):
        query = db.query(Tag)
        if busqueda:
            # ilike = búsqueda insensible a mayúsculas
            # busqueda="flor" encuentra "Flor", "FLOR", "flor pequeña"
            query = query.filter(Tag.nombre.ilike(f"%{busqueda}%"))
        return query.order_by(Tag.nombre)
 
    # Crear tag con normalización
    def crear(self, db: Session, nombre: str) -> Tag:
        # normaliza: elimina espacios y convierte a minúsculas
        nombre = nombre.lower().strip()
 
        existe = db.query(Tag).filter(Tag.nombre == nombre).first()
        if existe:
            raise HTTPException(status_code=400, detail="El tag ya existe")
 
        nuevo = Tag(nombre=nombre)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
 
    #  Actualizar nombre de un tag
    def actualizar(self, db: Session, tag_id: int, nombre: str) -> Tag:
        tag        = self.obtener_por_id(db, tag_id)
        tag.nombre = nombre.lower().strip()
        db.commit()
        db.refresh(tag)
        return tag
 
    #  Eliminar un tag
    def eliminar(self, db: Session, tag_id: int) -> dict:
        tag = self.obtener_por_id(db, tag_id)
        db.delete(tag)
        db.commit()
        return {"mensaje": f"Tag '{tag.nombre}' eliminado"}
 
    #  Tag más popular
    # Cuenta cuántas predicciones tiene cada tag usando
    # la tabla intermedia prediccion_tag y devuelve el de mayor conteo
    def mas_popular(self, db: Session) -> dict:
        resultado = (
            db.query(
                Tag,
                func.count(prediccion_tag.c.prediccion_id).label("total")
            )
            .join(prediccion_tag, Tag.id == prediccion_tag.c.tag_id)
            .group_by(Tag.id)
            .order_by(desc("total"))
            .first()
        )
 
        if not resultado:
            raise HTTPException(
                status_code=404,
                detail="No hay tags asociados a predicciones"
            )
 
        tag, total = resultado
        return {
            "id":                 tag.id,
            "nombre":             tag.nombre,
            "total_predicciones": total
        }
 
 
# Instancia única compartida
tag_repo = TagRepository()