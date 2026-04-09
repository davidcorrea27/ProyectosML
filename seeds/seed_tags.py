# seeds/seed_tags.py — 
#  Seed de tags
from models import Tag
from seeds.datos.tags import TAGS
 
 
def run(db):
    print("  Seeding tags...")
    for nombre in TAGS:
        nombre = nombre.lower().strip()
        existe = db.query(Tag).filter(Tag.nombre == nombre).first()
        if existe:
            print(f"    Tag '{nombre}' ya existe, saltando...")
            continue
 
        nuevo = Tag(nombre=nombre)
        db.add(nuevo)
        print(f"    Tag '{nombre}' creado")
 
    db.flush()
    print("  Tags listos")
 