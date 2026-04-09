# middlewares/middlewares.py 
# Centraliza todos los middlewares de la API

import time
import uuid
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

# configuración del logger — escribe en consola con timestamp
logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# IPs bloqueadas — agregar aquí las que quiero bloquear
IPS_BLOQUEADAS = set()   # ejemplo: {"192.168.1.100", "10.0.0.5"}


# Middleware 1 - Bloqueador de IPs
# Va primero para rechazar lo antes posible sin gastar recursos
async def bloquear_ips(request: Request, call_next):
    ip_cliente = request.client.host

    if ip_cliente in IPS_BLOQUEADAS:
        logger.warning(f"IP bloqueada intentó acceder: {ip_cliente}")
        return JSONResponse(
            status_code=403,
            content={"detail": f"Acceso denegado para IP {ip_cliente}"}
        )

    return await call_next(request)


# Middleware 2 - Request ID
# Genera un ID único por petición para rastrear errores
async def agregar_request_id(request: Request, call_next):
    # genera el ID único para esta petición
    request_id = str(uuid.uuid4())

    # lo guarda en el estado del request para que otros middlewares
    # o endpoints puedan accederlo con request.state.request_id
    request.state.request_id = request_id

    respuesta = await call_next(request)

    # lo agrega a la respuesta para que el cliente lo reciba
    respuesta.headers["X-Request-ID"] = request_id
    return respuesta


# Middleware 3 - Logging de peticiones
# Registra cada petición con su método, ruta, status y request ID
async def logging_peticiones(request: Request, call_next):
    # intenta obtener el request_id si el middleware anterior ya lo generó
    request_id = getattr(request.state, "request_id", "sin-id")

    logger.info(f"[{request_id}] → {request.method} {request.url.path}")

    respuesta = await call_next(request)

    logger.info(f"[{request_id}] ← {request.method} {request.url.path} | status: {respuesta.status_code}")

    return respuesta


# Middleware 4 - Cálculo de tiempo de proceso
# Mide cuánto tarda cada petición y lo agrega como header
# Útil para detectar endpoints lentos modelo ML tardando
async def tiempo_proceso(request: Request, call_next):
    inicio    = time.time()
    respuesta = await call_next(request)
    duracion  = time.time() - inicio

    # agrega el tiempo en milisegundos como header de la respuesta
    # visible en Swagger en la sección "Response headers"
    respuesta.headers["X-Process-Time-ms"] = str(round(duracion * 1000, 2))
    return respuesta