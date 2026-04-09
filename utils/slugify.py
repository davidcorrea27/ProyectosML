import re
import uuid
from datetime import datetime
 
 
def slugify(texto: str) -> str:
    # convierte a minúsculas
    slug = texto.lower()
 
    # reemplaza cualquier carácter que no sea letra o número por guión
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
 
    # elimina guiones al inicio y final
    slug = slug.strip('-')
 
    # agrega fecha y fragmento único — garantiza que dos predicciones
    # de la misma especie en el mismo día tengan slugs diferentes
    fecha    = datetime.now().strftime("%Y%m%d")
    uniqueid = str(uuid.uuid4())[:8]
 
    return f"{slug}-{fecha}-{uniqueid}"