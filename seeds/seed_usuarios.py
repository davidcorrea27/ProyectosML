# seeds/seed_usuarios.py 
# Seed de usuarios
from models import Usuario
from security import hash_password
from seeds.datos.usuarios import USUARIOS
 
 
def run(db):
    print("  Seeding usuarios...")
    for datos in USUARIOS:
        # verifica si ya existe antes de insertar — idempotencia
        existe = db.query(Usuario).filter(Usuario.email == datos["email"]).first()
        if existe:
            print(f"    Usuario {datos['email']} ya existe, saltando...")
            continue
 
        nuevo = Usuario(
            nombre          = datos["nombre"],
            email           = datos["email"],
            hashed_password = hash_password(datos["password"]),
            rol             = datos["rol"],
            activo          = True
        )
        db.add(nuevo)
        print(f"    Usuario {datos['email']} creado con rol '{datos['rol']}'")
 
    db.flush()  # envía los inserts sin hacer commit todavía
    print("  Usuarios listos")
 