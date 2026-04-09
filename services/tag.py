# services/tag.py 
#  Servicio de paginación
# Centraliza la lógica de paginación reutilizable
# No toca DB directamente trabaja sobre queries de SQLAlchemy

from math import ceil
 
 
class TagService:
    #  Servicio de paginación
    # Recibe una query de SQLAlchemy (sin ejecutar todavía)
    # Aplica paginación y devuelve los resultados estructurados
    def paginar(self, query, pagina: int, por_pagina: int) -> dict:
        # cuenta el total sin traer todos los datos
        total      = query.count()
        total_pags = ceil(total / por_pagina) if total > 0 else 1
 
        # valida que la página pedida existe
        if pagina > total_pags and total > 0:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"La página {pagina} no existe")
 
        # aplica offset y limit — equivale a SQL: OFFSET x LIMIT y
        inicio = (pagina - 1) * por_pagina
        items  = query.offset(inicio).limit(por_pagina).all()
 
        return {
            "items":      items,
            "total":      total,
            "pagina":     pagina,
            "total_pags": total_pags,
            "por_pagina": por_pagina
        }
 
 
# Instancia única compartida por todos los routers
tag_service = TagService()