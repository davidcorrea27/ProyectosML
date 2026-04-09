from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
# Schema para POST y PUT
class IrisFeatures(BaseModel):
    sepal_length: float = Field(gt=0, lt=10, description="Largo del sépalo en cm")
    sepal_width:  float = Field(gt=0, lt=10, description="Ancho del sépalo en cm")
    petal_length: float = Field(gt=0, lt=10, description="Largo del pétalo en cm")
    petal_width:  float = Field(gt=0, lt=10, description="Ancho del pétalo en cm")

    # Validación personalizada
    # Regla biológica: el pétalo no puede ser más largo que el sépalo
    @field_validator("petal_length")
    @classmethod
    def petalo_menor_que_sepalo(cls, petal_length, values):
        sepal = values.data.get("sepal_length")
        if sepal is not None and petal_length > sepal:
            raise ValueError("petal_length no puede ser mayor que sepal_length")
        return petal_length


 # TAG SCHEMAS — schemas más completos para tags

# Schema para crear un tag
class TagCreate(BaseModel):
    nombre: str

# para actualizar el nombre de un tag existente
class TagUpdate(BaseModel):
    nombre: str



# SCHEMAS DE RESPUESTA (lo que la API devuelve)
# model_config = ConfigDict(from_attributes=True)
# Esto le dice a Pydantic que puede leer objetos SQLAlchemy
# no solo diccionarios
# ahora incluye total_predicciones
class TagResponse(BaseModel):
    id:                 int
    nombre:             str
    total_predicciones: int = 0   # cuántas predicciones usan este tag
 
    model_config = ConfigDict(from_attributes=True)

# respuesta específica para el tag más popular
class TagPopularResponse(BaseModel):
    id:                 int
    nombre:             str
    total_predicciones: int   # el conteo que lo hace popular
 
    model_config = ConfigDict(from_attributes=True)

#  respuesta paginada para el listado de tags
class TagsPageResponse(BaseModel):
    items:      List[TagResponse] 
    total:      int
    pagina:     int
    total_pags: int
    por_pagina: int
 
#   Category Schemas
 
# Para crear una categoría
class CategoriaCreate(BaseModel):
    nombre:      str
    descripcion: Optional[str] = None   # campo opcional
 
# Para actualizar una categoría
class CategoriaUpdate(BaseModel):
    nombre:      Optional[str] = None
    descripcion: Optional[str] = None
 
# Lo que devuelve la API sobre una categoría
class CategoriaResponse(BaseModel):
    id:                 int
    nombre:             str
    descripcion:        Optional[str] = None
    total_predicciones: int = 0
 
    model_config = ConfigDict(from_attributes=True)
 
# Para listado paginado de categorías — reutiliza TagsPageResponse lógica
class CategoriasPageResponse(BaseModel):
    items:      List[CategoriaResponse]
    total:      int
    pagina:     int
    total_pags: int
    por_pagina: int
 





# PREDICCION SCHEMAS 
# Schema para predecir con autor y tags opcionales
# PrediccionCreate ahora acepta categoria_id
class PrediccionCreate(BaseModel):
    features:   IrisFeatures
    #usuario_id: Optional[int] = None          # puede predecir sin usuario
    tags:       Optional[List[str]] = [] # lista de nombres de tags
    categoria_id: Optional[int] = None   # 
    






# RESPONSE SCHEMAS
# MODELOS DE RESPUESTA lo que devuelve la API
# Modelo de respuesta
class ClaseResponse(BaseModel):
    clase_id: int
    clase_nombre: str



class MuestraResponse(BaseModel):
    muestra_id: int
    mensaje: str
    nuevos_valores: IrisFeatures 


class MuestrasResponse(BaseModel):
    pagina: int
    por_pagina: int
    total_muestras: int
    orden: str
    datos: list


#  User Schemas
# Se reemplaza UsuarioCreate (solo nombre+email)
# por schemas específicos para registro, login y respuesta

 #Lo que manda el usuario para registrarse
# Ahora incluye password además de nombre y email
class UserRegister(BaseModel):
    nombre:   str
    email:    str
    password: str    # texto plano — se hashea en security.py antes de guardar


# Lo que manda el usuario para hacer login
class UserLogin(BaseModel):
    email:    str
    password: str    # texto plano — se compara contra el hash en DB

# Lo que devuelve la API después de un login exitoso
# Security Tokens
class TokenResponse(BaseModel):
    access_token: str    # el JWT generado
    token_type:   str    # siempre "bearer"

# Lo que devuelve la API sobre un usuario
# NUNCA incluye hashed_password
class UsuarioResponse(BaseModel):
    id:     int
    nombre: str
    email:  str
    rol:    str      # "user" o "admin" 
    activo: bool     # nuevo
 
    model_config = ConfigDict(from_attributes=True)

# Para que un admin cambie el rol de otro usuario
# User Router SetRole
class SetRoleRequest(BaseModel):
    email:   str
    nuevo_rol: str    # "user" o "admin"


# PrediccionResponse — se actualiza para usar UsuarioResponse nuevo
class PrediccionResponse(BaseModel):
    id:           int
    slug:         Optional[str] = None  
    especie:      str
    clase_id:     int
    fecha:        datetime
    sepal_length: float
    sepal_width:  float
    petal_length: float
    petal_width:  float
    usuario:      Optional[UsuarioResponse] = None
    tags:         List[TagResponse]         = []
    categoria:    Optional[CategoriaResponse] = None  
 
    model_config = ConfigDict(from_attributes=True)
