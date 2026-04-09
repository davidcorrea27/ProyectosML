from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
 
from database import get_db
from models import Usuario
from schemas import (
    UserRegister, UsuarioResponse,
    TokenResponse, SetRoleRequest
)
from security import hash_password, verify_password, create_token, get_current_user, require_role
 
# APIRouter — es como un app pequeño que se conecta al app principal
# prefix="/auth" → todos los endpoints de este archivo empiezan con /auth
# tags=["Auth"]  → aparecen bajo la categoría Auth en Swagger
router = APIRouter(prefix="/auth", tags=["Auth"])
 
 
# Registro
# Recibe nombre, email y password en texto plano
# Hashea la contraseña antes de guardar
# Guarda con rol="user" por defecto
@router.post("/register", response_model=UsuarioResponse, summary="Registra un nuevo usuario")
def register(usuario: UserRegister, db: Session = Depends(get_db)):
    #  User Repository: verificar que el email no exista
    existe = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
 
    nuevo = Usuario(
        nombre          = usuario.nombre,
        email           = usuario.email,
        hashed_password = hash_password(usuario.password),  # Tema 182 - nunca guardar texto plano
        rol             = "user",
        activo          = True
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
 
 
#  Login
#  OAuth2PasswordRequestForm para el formulario de Swagger
# OAuth2PasswordRequestForm espera campos "username" y "password"
# en formato de formulario (no JSON) — requerimiento del estándar OAuth2
# Usamos username como email
@router.post("/login", response_model=TokenResponse, summary="Login y obtención de token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #  buscar el usuario en DB
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
 
    # Verificar que existe y que la contraseña es correcta
    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
 
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
 
    #  crear el JWT con email y rol adentro
    token = create_token({"sub": usuario.email, "rol": usuario.rol})
 
    return TokenResponse(access_token=token, token_type="bearer")
 
 
# Información del usuario autenticado
# Endpoint protegido: requiere token válido
# get_current_user decodifica el token y devuelve el usuario

@router.get("/me", response_model=UsuarioResponse, summary="Información del usuario autenticado")
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario
 
 
#  SetRole
# Solo un admin puede cambiar el rol de otro usuario
# require_role("admin") verifica que quien llama sea admin
@router.put("/set-role", response_model=UsuarioResponse, summary="Cambia el rol de un usuario (solo admin)")
def set_role(
    request: SetRoleRequest,
    db:      Session = Depends(get_db),
    _:       Usuario = Depends(require_role("admin"))   # _ = no usamos el objeto, solo verificamos
):
    if request.nuevo_rol not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Rol inválido. Usa 'user' o 'admin'")
 
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
 
    usuario.rol = request.nuevo_rol
    db.commit()
    db.refresh(usuario)
    return usuario