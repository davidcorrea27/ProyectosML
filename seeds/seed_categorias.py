# seeds/seed_categorias.py — 
# Seed de categorías
from models import Categoria
from seeds.datos.categorias import CATEGORIAS
 
 
def run(db):
    print("  Seeding categorías...")
    for datos in CATEGORIAS:
        nombre = datos["nombre"].lower().strip()
        existe = db.query(Categoria).filter(Categoria.nombre == nombre).first()
        if existe:
            print(f"    Categoría '{nombre}' ya existe, saltando...")
            continue
 
        nueva = Categoria(
            nombre      = nombre,
            descripcion = datos["descripcion"]
        )
        db.add(nueva)
        print(f"    Categoría '{nombre}' creada")
 
    db.flush()
    print("  Categorías listas")
 