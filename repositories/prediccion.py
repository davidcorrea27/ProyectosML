# repositories/prediccion.py — ARCHIVO NUEVO 
# Arquitectura de capas
# PostRepository Obtener por ID
#  PostRepository Búsquedas (Search)
# PostRepository Lista de tags
#  PostRepository Ensure author y tags
#  PostRepository Crear post
#  PostRepository put y delete
# Esta clase centraliza TODA la lógica de base de datos
# relacionada con predicciones. Los routers no tocan SQL directamente,
# solo llaman métodos de esta clase.
#  genera slug automáticamente




from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Prediccion, Usuario, Tag
from utils.slugify import slugify
 

class PrediccionRepository:
    # Obtener predicción por ID
    def obtener_por_id(self, db: Session, prediccion_id: int) -> Prediccion:
        pred = db.query(Prediccion).filter(Prediccion.id == prediccion_id).first()
        if not pred:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")
        return pred
        
         # obtener predicción por slug
    def obtener_por_slug(self, db: Session, slug: str) -> Prediccion:
        pred = db.query(Prediccion).filter(Prediccion.slug == slug).first()
        if not pred:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")
        return pred

    
    # Búsquedas con filtros opcionales
    # Centraliza toda la lógica de filtrado y búsqueda
    def buscar(
        self,
        db:      Session,
        especie: str = None,
        tag:     str = None
    ) -> list:
        query = db.query(Prediccion)
 
        if especie:
            query = query.filter(Prediccion.especie == especie)
 
        if tag:
            # filtrar por tag usando la relación muchos a muchos
            query = query.join(Prediccion.tags).filter(Tag.nombre == tag)
 
        return query.all()
 
    #  Ensure: garantiza que el usuario existe
    # Si no existe lanza HTTPException antes de continuar
    def ensure_usuario(self, db: Session, usuario_id: int) -> Usuario:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
     #  Ensure: garantiza que el tag existe
    def ensure_tag(self, db: Session, nombre_tag: str) -> Tag:
        tag = db.query(Tag).filter(Tag.nombre == nombre_tag).first()
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag '{nombre_tag}' no existe")
        return tag
    
    
    
    # Crear predicción en DB
    # Recibe el objeto Prediccion ya construido y los tags
    # Separa la lógica de DB de la lógica de ML del router
    # ahora acepta categoria_id
    # crear() ahora genera el slug automáticamente
    # Antes: nueva.slug no existía
    # Ahora: se genera desde la especie predicha antes de guardar
    def crear(self, db: Session, 
              nueva: Prediccion, tags: list = [],
             categoria_id: int = None) -> Prediccion:
         # primero valida todos los tags antes de guardar nada
        # agregar tags a la tabla intermedia
        tags_validados = []
        for nombre_tag in tags:
            tag = self.ensure_tag(db, nombre_tag)
            tags_validados.append(tag)
 
        # asigna la categoría si viene
        if categoria_id:
            nueva.categoria_id = categoria_id

         # genera el slug basado en la especie predicha
        # "setosa" → "setosa-20240115-a3f8c2d1"
        nueva.slug = slugify(nueva.especie)
 
 
        # asigna tags y guarda todo en una sola transacción
        nueva.tags = tags_validados
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva
     # Actualizar tags de una predicción
    def actualizar_tags(self, db: Session, prediccion_id: int, tags: list) -> Prediccion:
        pred = self.obtener_por_id(db, prediccion_id)
 
        # reemplaza todos los tags actuales por los nuevos
        pred.tags = []
        for nombre_tag in tags:
            tag = self.ensure_tag(db, nombre_tag)
            pred.tags.append(tag)
 
        db.commit()
        db.refresh(pred)
        return pred
     #  Eliminar predicción
    def eliminar(self, db: Session, prediccion_id: int) -> dict:
        pred = self.obtener_por_id(db, prediccion_id)
        db.delete(pred)
        db.commit()
        return {"mensaje": f"Predicción {prediccion_id} eliminada"}
 
 
# Instancia única que usarán todos los routers
# En vez de crear la clase cada vez, se importa esta instancia
prediccion_repo = PrediccionRepository()