# routers/tags.py
#  Endpoint crear tags
#  Listado de tags con paginación
#  Endpoints Update y Delete
#  Endpoint tag más popular


from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import Optional
 
from database import get_db
from models import Usuario
from schemas import TagCreate, TagUpdate, TagResponse, TagPopularResponse, TagsPageResponse
from security import get_current_user, require_role
from repositories.tag import tag_repo
from services.tag import tag_service
 
router = APIRouter(prefix="/tags", tags=["Tags"])
 
 
# Listar tags con paginación y búsqueda
@router.get(
    "",
    response_model=TagsPageResponse,
    summary="Lista todos los tags con paginación"
)
def listar_tags(
    pagina:     int           = Query(default=1,  ge=1),
    por_pagina: int           = Query(default=10, ge=1, le=50),
    busqueda:   Optional[str] = Query(default=None, description="Buscar por nombre"),
    db:         Session       = Depends(get_db)
):
    # obtiene la query sin ejecutar
    query = tag_repo.listar_query(db, busqueda=busqueda)
    # el servicio aplica paginación y devuelve los resultados
    return tag_service.paginar(query, pagina, por_pagina)
 
 
#  Tag más popular
#  este endpoint debe ir ANTES de /tags/{tag_id}
# porque FastAPI lee las rutas en orden y "/popular" podría
# confundirse con un tag_id si va después
@router.get(
    "/popular",
    response_model=TagPopularResponse,
    summary="Obtiene el tag más usado en predicciones"
)
def tag_mas_popular(db: Session = Depends(get_db)):
    return tag_repo.mas_popular(db)
 
 
# Crear tag
@router.post(
    "",
    response_model=TagResponse,
    summary="Crea un nuevo tag"
)
def crear_tag(
    tag: TagCreate,
    db:  Session = Depends(get_db),
    _:   Usuario = Depends(get_current_user)   # requiere autenticación
):
    return tag_repo.crear(db, tag.nombre)
 
 
#  Actualizar tag
@router.put(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Actualiza el nombre de un tag"
)
def actualizar_tag(
    tag_id: int       = Path(ge=1),
    tag:    TagUpdate = ...,
    db:     Session   = Depends(get_db),
    _:      Usuario   = Depends(get_current_user)
):
    return tag_repo.actualizar(db, tag_id, tag.nombre)
 
 
#  Eliminar tag (solo admin)
@router.delete(
    "/{tag_id}",
    summary="Elimina un tag (solo admin)"
)
def eliminar_tag(
    tag_id: int     = Path(ge=1),
    db:     Session = Depends(get_db),
    _:      Usuario = Depends(require_role("admin"))
):
    return tag_repo.eliminar(db, tag_id)
 