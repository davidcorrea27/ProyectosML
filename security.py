# Security Tokens
#  Security Hash Password
# Security Require Role
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
 
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRE_MINUTES = int(os.getenv("EXPIRE_MINUTES", 30))
# Hash Password
# CryptContext configura el algoritmo de hashing
# bcrypt es el estándar actual para contraseñas
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
# Token por formulario Swagger
# OAuth2PasswordBearer le dice a FastAPI dónde está el endpoint
# de login. Esto activa el botón "Authorize" en Swagger.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
 
 
#  Función para hashear una contraseña
# "1234"  →  "$2b$12$abc..."
# Es irreversible: no se puede recuperar la contraseña original
def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)
 
 
#  Función para verificar una contraseña
# Compara el texto plano contra el hash guardado en DB
# Devuelve True si coinciden, False si no
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt_context.verify(password, hashed)

# Función para crear un JWT
# Recibe un diccionario con los datos del usuario
# Agrega la fecha de expiración
# Firma el token con SECRET_KEY
# Devuelve el string del JWT
def create_token(data: dict) -> str:
    payload = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    payload.update({"exp": expiracion})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
 
 
#  Función para leer y validar un token
# Se inyecta automáticamente en endpoints protegidos
# Lee el token del header Authorization
# Decodifica y verifica que no haya expirado
# Devuelve el email del usuario dueño del token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from models import Usuario  # import aquí para evitar importación circular
 
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
 
    # Busca el usuario en DB para confirmar que existe y está activo
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not usuario.activo:
        raise credentials_exception
    return usuario
 
 
#  Require Role
# Fábrica de dependencias: devuelve una función que verifica
# que el usuario actual tenga el rol requerido
# Uso: Depends(require_role("admin"))
def require_role(rol: str):
    def verificar(usuario=Depends(get_current_user)):
        if usuario.rol != rol:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Se requiere rol '{rol}'"
            )
        return usuario
    return verificar