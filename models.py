#  Modelos declarativos (tablas como clases Python)
#  Relación uno a muchos (autor)
#  Relación muchos a muchos (tags)
#  Agrega modelo Categoria y FK en Prediccion
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
 
 
#  Tabla intermedia para relación muchos a muchos
# Una predicción puede tener muchos tags
# Un tag puede estar en muchas predicciones
# Esta tabla no es una clase, solo conecta las dos tablas
prediccion_tag = Table(
    "prediccion_tag",          # nombre de la tabla en la DB
    Base.metadata,
    Column("prediccion_id", Integer, ForeignKey("predicciones.id")),
    Column("tag_id",        Integer, ForeignKey("tags.id"))
)
 
 
#  Tabla usuarios (el "uno" en uno a muchos)
# Un usuario puede tener muchas predicciones
# Se agregan 3 columnas nuevas a Usuario:
#   hashed_password contraseña hasheada, nunca texto plano
#   rol             "user" o "admin"
#   activo          para desactivar sin borrar de la DB
class Usuario(Base):
    __tablename__ = "usuarios"
 
    id       = Column(Integer, primary_key=True, index=True)
    nombre   = Column(String,  nullable=False)
    email    = Column(String,  unique=True, nullable=False)
    
    # Nuevo 
    hashed_password = Column(String,  nullable=False)
    rol             = Column(String,  default="user", nullable=False)
    activo          = Column(Boolean, default=True,   nullable=False)
 
    # relationship: permite acceder a usuario.predicciones
    # y desde prediccion.usuario
    predicciones = relationship("Prediccion", back_populates="usuario")
 
 
# T Tabla tags (etiquetas para las predicciones)
class Tag(Base):
    __tablename__ = "tags"
 
    id     = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
 
    # relationship: permite acceder a tag.predicciones
    predicciones = relationship(
        "Prediccion",
        secondary=prediccion_tag,   # usa la tabla intermedia
        back_populates="tags"
    )
 
 
# Tabla Categoria
# Relación uno a muchos con Prediccion:
# una categoría tiene muchas predicciones
# una predicción pertenece a UNA sola categoría
class Categoria(Base):
    __tablename__ = "categorias"
 
    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String,  unique=True, nullable=False)
    descripcion = Column(String,  nullable=True)   # campo opcional
 
    # permite acceder a categoria.predicciones
    predicciones = relationship("Prediccion", back_populates="categoria")



#  Tabla principal: predicciones
#  ForeignKey a usuarios (uno a muchos)
# - Relación a tags (muchos a muchos)
class Prediccion(Base):
    __tablename__ = "predicciones"
 
    id           = Column(Integer, primary_key=True, index=True)
    sepal_length = Column(Float,   nullable=False)
    sepal_width  = Column(Float,   nullable=False)
    petal_length = Column(Float,   nullable=False)
    petal_width  = Column(Float,   nullable=False)
    especie      = Column(String,  nullable=False)
    clase_id     = Column(Integer, nullable=False)
    fecha        = Column(DateTime, default=datetime.now)
    
    # slug único para identificar predicciones en URLs
    slug = Column(String, unique=True, nullable=True, index=True)
 
    #  Relación uno a muchos con Usuario
    # nullable=True  la predicción puede hacerse sin usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario    = relationship("Usuario", back_populates="predicciones")
 
    # Relación muchos a muchos con Tag
    tags = relationship(
        "Tag",
        secondary=prediccion_tag,   # usa la tabla intermedia
        back_populates="predicciones"
    )

 # FK a categorias, nullable porque puede no tener categoría
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    categoria    = relationship("Categoria", back_populates="predicciones")
 