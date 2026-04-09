from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from typing import Optional, List
 
from database import get_db
from models import Prediccion, Usuario
from schemas import PrediccionCreate, PrediccionResponse
from security import get_current_user, require_role
from repositories.prediccion import prediccion_repo
 
router = APIRouter(tags=["Predicción"])
 
# Modelo ML — se inicializa una vez al importar el router
iris  = load_iris()
model = KNeighborsClassifier()
model.fit(iris.data, iris.target)
 
#  Crear predicción
# El router hace la predicción ML y construye el objeto
# El repository se encarga de guardarlo en DB
@router.post(
    "/predecir",
    response_model=PrediccionResponse,
    summary="Predice la especie y guarda en DB",
    description="Requiere autenticación. El usuario se asocia desde el token."
)
def predecir(
    payload:        PrediccionCreate,
    db:             Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user) #  requiere token
):
    f    = payload.features
    pred = model.predict([[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]])[0]
 
    # Construye el objeto — lógica de ML en el router
    nueva = Prediccion(
        sepal_length = f.sepal_length,
        sepal_width  = f.sepal_width,
        petal_length = f.petal_length,
        petal_width  = f.petal_width,
        especie      = iris.target_names[pred],
        clase_id     = int(pred),
        usuario_id   = usuario_actual.id # se asocia automáticamente al usuario del token
    )
    # El repository guarda en DB y agrega los tags
    #     pasa categoria_id al repository
    return prediccion_repo.crear(db, nueva, tags = payload.tags or [], 
                                 categoria_id = payload.categoria_id)
 
 
# Listar predicciones con filtros
@router.get(
    "/predicciones",
    response_model=List[PrediccionResponse],
    summary="Lista predicciones guardadas",
    description="Requiere autenticación. Filtra por especie o tag."
)
def listar_predicciones(
    especie: Optional[str] = Query(default=None, description="Filtrar por especie"),
    tag:     Optional[str] = Query(default=None, description="Filtrar por tag"),
    db:      Session = Depends(get_db),
    _:       Usuario = Depends(get_current_user)    # requiere token
):
    # delega la búsqueda al repository
    return prediccion_repo.buscar(db, especie=especie, tag=tag)
 
 
#  Obtener predicción por ID
@router.get(
    "/predicciones/{prediccion_id}",
    response_model=PrediccionResponse,
    summary="Obtiene una predicción por ID"
)
def obtener_prediccion(
    prediccion_id: int = Path(ge=1),
    db:  Session = Depends(get_db),
    _:   Usuario = Depends(get_current_user)
):
    #  delega al repository
    return prediccion_repo.obtener_por_id(db, prediccion_id)



 #  buscar predicción por slug
# Va ANTES de /{prediccion_id} para evitar que FastAPI interprete
# "slug" como un número entero
@router.get(
    "/predicciones/slug/{slug}",
    response_model=PrediccionResponse,
    summary="Obtiene una predicción por su slug"
)
def obtener_por_slug(
    slug: str,
    db:   Session = Depends(get_db),
    _:    Usuario = Depends(get_current_user)
):
    return prediccion_repo.obtener_por_slug(db, slug)
 






#  Actualizar tags de una predicción
@router.put(
    "/predicciones/{prediccion_id}/tags",
    response_model=PrediccionResponse,
    summary="Actualiza los tags de una predicción"
)
def actualizar_tags(
    prediccion_id: int       = Path(ge=1),
    tags:          List[str] = [],
    db:  Session = Depends(get_db),
    _:   Usuario = Depends(get_current_user) # requiere token
):
    #  delega al repository
    return prediccion_repo.actualizar_tags(db, prediccion_id, tags)
 
 
#  Eliminar predicción (solo admin)
@router.delete(
    "/predicciones/{prediccion_id}",
    summary="Elimina una predicción (solo admin)"
)
def eliminar_prediccion(
    prediccion_id: int = Path(ge=1),
    db:  Session = Depends(get_db),
    _:   Usuario = Depends(require_role("admin")) # solo admin
):
    #  delega al repository
    return prediccion_repo.eliminar(db, prediccion_id)