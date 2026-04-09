#  Montar routers en main.py
# Con arquitectura de capas main.py queda muy limpio
# solo inicializa la app, crea tablas y conecta los routers

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware   
from typing import Optional, List
from sklearn.datasets import load_iris
 
from database import engine, Base
from schemas import ClaseResponse, MuestraResponse, MuestrasResponse, IrisFeatures
 #  importar y montar routers conectar el router de autenticación al app principal
from routers.users        import router as auth_router
from routers.predicciones import router as predicciones_router
from routers.tags         import router as tags_router          
from routers.categorias   import router as categorias_router 

#importar los middlewares personalizados
from middlewares.middlewares import (
    bloquear_ips,
    agregar_request_id,
    logging_peticiones,
    tiempo_proceso
)
# - importar seguridad
#from security import get_current_user, require_role
 

# Crear todas las tablas en PostgreSQL al arrancar
Base.metadata.create_all(bind=engine)

# Inicializar app y modelo
app = FastAPI()

# MIDDLEWARES 
#  se aplican de abajo hacia arriba en la entrada
# y de arriba hacia abajo en la salida
 
# CORS  permite que frontends externos consuman la API
# Tema Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # en producción: ["https://mi-frontend.com"]
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)
 
# Middlewares personalizados — se registran con app.middleware("http")
#  Bloqueador de IPs
app.middleware("http")(bloquear_ips)
 
#  Request ID — genera ID único por petición
app.middleware("http")(agregar_request_id)
 
# Logging — registra todas las peticiones en consola
app.middleware("http")(logging_peticiones)
 
#  Tiempo de proceso — agrega X-Process-Time-ms a cada respuesta
app.middleware("http")(tiempo_proceso)
 









#registrar los dos routers
# registrar el router de auth
# Todos sus endpoints quedan disponibles bajo /auth/...
app.include_router(auth_router)
app.include_router(predicciones_router)
app.include_router(tags_router)  # NUEVO
app.include_router(categorias_router)     # NUEVO

iris = load_iris()








# GET básico  
@app.get("/", summary="Raíz de la API", tags=["General"])
def root():
    return {"mensaje": "API del dataset Iris CREADO POR DAVID, ESTA ES MI PRIMERA API"}


# GET con datos  
@app.get(
    "/clases",
    summary="Lista todas las clases del dataset",
    description="Retorna los nombres de las 3 especies de Iris y el total de muestras disponibles.",
    tags=["Dataset"]
)
def get_clases():
    return {
        "clases": list(iris.target_names),
        "total_muestras": len(iris.data)
    }
# Query params 
# muestra las primeras N muestras del dataset
# Uso: /muestras?limite=5
@app.get(
    "/muestras",
    response_model=MuestrasResponse,
    summary="Obtiene muestras del dataset con paginación",
    description="Permite paginar, ordenar y filtrar por especie. El parámetro 'limite' está deprecado, usa 'por_pagina'.",
    tags=["Dataset"]
)
def get_muestras(
    #  Query() valida directamente en la URL
    pagina: int = Query(default=1, ge=1, description="Número de página"),
    por_pagina: int = Query(default=10, ge=1, le=50, description="Muestras por página"),
 
    # Orden de los resultados
    orden: str = Query(default="asc", description="Orden: 'asc' o 'desc'"),
 
    #  Lista de especies para filtrar
    # Uso: /muestras?especies=setosa&especies=virginica
    especies: List[str] = Query(default=[], description="Filtrar por especies (puede ser más de una)"),
 
    #  Parámetro viejo marcado como deprecated
    limite: Optional[int] = Query(default=None, deprecated=True, description="Obsoleto, usa por_pagina")
):
    if orden not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="orden debe ser 'asc' o 'desc'")
 
    datos = list(zip(iris.data.tolist(), iris.target.tolist()))
 
    # Filtrar por especies si se mandaron
    nombres_especies = list(iris.target_names)
    if especies:
        especies_invalidas = [e for e in especies if e not in nombres_especies]
        if especies_invalidas:
            raise HTTPException(
                status_code=400,
                detail=f"Especies inválidas: {especies_invalidas}. Válidas: {nombres_especies}"
            )
        ids_validos = [nombres_especies.index(e) for e in especies]
        datos = [(d, t) for d, t in datos if t in ids_validos]
 
    # Ordenar por primer feature (sepal_length)
    datos = sorted(datos, key=lambda x: x[0][0], reverse=(orden == "desc"))
 
    # Paginación
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    pagina_datos = datos[inicio:fin]
 
    if not pagina_datos:
        raise HTTPException(status_code=404, detail=f"La página {pagina} no existe.")
 
    return MuestrasResponse(
        pagina=pagina,
        por_pagina=por_pagina,
        total_muestras=len(datos),
        orden=orden,
        datos=[{"medidas": d, "especie": nombres_especies[t]} for d, t in pagina_datos]
    )
 

# Path parameter  
# devuelve info de una clase por su ID (0, 1 o 2)
# Uso: /clase/0
@app.get(
    "/clase/{clase_id}",
    response_model=ClaseResponse,
    summary="Obtiene información de una clase por ID",
    description="Retorna el nombre de la especie según su ID. Valores válidos: 0 (setosa), 1 (versicolor), 2 (virginica).",
    tags=["Dataset"]
)

def get_clase(
    # Path() valida el path param directamente, elimina el if manual
    clase_id: int = Path(ge=0, le=2, description="ID de la clase: 0, 1 o 2")
):
    return ClaseResponse(
        clase_id=clase_id,
        clase_nombre=iris.target_names[clase_id]
    )


# PUT con validación de path param
#  Path() en muestra_id
@app.put(
    "/muestra/{muestra_id}",
    response_model=MuestraResponse,
    summary="Actualiza las medidas de una muestra",
    description="Recibe el índice de una muestra (0-149) y nuevas medidas. Simulado: el dataset Iris es de solo lectura.",
    tags=["Dataset"]
)
def actualizar_muestra(
    muestra_id: int = Path(ge=0, le=149, description="Índice de la muestra (0 a 149)"),
    features: IrisFeatures = None
):
    return MuestraResponse(
        muestra_id=muestra_id,
        mensaje=f"Muestra {muestra_id} actualizada (simulado)",
        nuevos_valores=features
    )



# DELETE  
# simula eliminar una muestra por su índice
@app.delete(
    "/muestra/{muestra_id}",
    summary="Elimina una muestra por su índice",
    description="Simulado: el dataset Iris es de solo lectura. Valida que el índice esté entre 0 y 149.",
    tags=["Dataset"]
)
def eliminar_muestra(
    muestra_id: int = Path(ge=0, le=149, description="Índice de la muestra (0 a 149)")
):
    return {"mensaje": f"Muestra {muestra_id} eliminada (simulado)"}
