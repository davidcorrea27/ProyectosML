# routers/categorias.py 
#  Category Router
# Montar en main.py


from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import Optional
 
from database import get_db
from models import Usuario
from schemas import (
    CategoriaCreate, CategoriaUpdate,
    CategoriaResponse, CategoriasPageResponse
)
from security import get_current_user, require_role
from repositories.categoria import categoria_repo
from services.tag import tag_service   # reutilizamos el mismo servicio de paginación
 
router = APIRouter(prefix="/categorias", tags=["Categorías"])
 
 
# Listar categorías con paginación y búsqueda
@router.get(
    "",
    response_model=CategoriasPageResponse,
    summary="Lista todas las categorías con paginación"
)
def listar_categorias(
    pagina:     int           = Query(default=1,  ge=1),
    por_pagina: int           = Query(default=10, ge=1, le=50),
    busqueda:   Optional[str] = Query(default=None, description="Buscar por nombre"),
    db:         Session       = Depends(get_db)
):
    query = categoria_repo.listar_query(db, busqueda=busqueda)
    return tag_service.paginar(query, pagina, por_pagina)
 
 
# Categoría más popular — va ANTES de /{categoria_id}
@router.get(
    "/popular",
    response_model=CategoriaResponse,
    summary="Obtiene la categoría con más predicciones"
)
def categoria_mas_popular(db: Session = Depends(get_db)):
    return categoria_repo.mas_popular(db)
 
 
# Crear categoría — solo admin
@router.post(
    "",
    response_model=CategoriaResponse,
    summary="Crea una nueva categoría (solo admin)"
)
def crear_categoria(
    categoria: CategoriaCreate,
    db:        Session = Depends(get_db),
    _:         Usuario = Depends(require_role("admin"))   # solo admin crea categorías
):
    return categoria_repo.crear(db, categoria.nombre, categoria.descripcion)
 
 
# Actualizar categoría — solo admin
@router.put(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Actualiza una categoría (solo admin)"
)
def actualizar_categoria(
    categoria_id: int            = Path(ge=1),
    categoria:    CategoriaUpdate = ...,
    db:           Session         = Depends(get_db),
    _:            Usuario         = Depends(require_role("admin"))
):
    return categoria_repo.actualizar(
        db,
        categoria_id,
        nombre      = categoria.nombre,
        descripcion = categoria.descripcion
    )
 
 
# Eliminar categoría — solo admin
@router.delete(
    "/{categoria_id}",
    summary="Elimina una categoría (solo admin)"
)
def eliminar_categoria(
    categoria_id: int     = Path(ge=1),
    db:           Session = Depends(get_db),
    _:            Usuario = Depends(require_role("admin"))
):
    return categoria_repo.eliminar(db, categoria_id)