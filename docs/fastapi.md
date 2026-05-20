# FastAPI

FastAPI es un framework web moderno para Python (3.8+) orientado a construir APIs con alto rendimiento. Se basa en **Starlette** (ASGI) y **Pydantic** (validacion de datos).

## Por que FastAPI

- Rendimiento comparable a NodeJS y Go gracias a ASGI y async/await.
- Validacion y serializacion automatica con Pydantic.
- Generacion automatica de documentacion interactiva: Swagger UI en `/docs` y ReDoc en `/redoc`.
- Tipado estatico en Python: mejora la experiencia en el IDE y detecta errores antes.

## Estructura minima

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"id": 1, **item.dict()}
```

## Modelos Pydantic

- Definen el esquema de entrada y salida.
- FastAPI valida automáticamente; si el body no encaja, devuelve HTTP 422.
- Soportan valores por defecto, campos opcionales (`Optional[str] = None`) y validadores personalizados.

## Manejo de errores

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]
```

## Exception handlers globales

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(status_code=422, content={"error": str(exc)})

@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"error": "internal_error"})
```

## Ciclo de vida (startup/shutdown)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialización (antes de arrancar)
    yield
    # Código de limpieza (al cerrar)

app = FastAPI(lifespan=lifespan)
```

## Arrancar el servidor

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

- `--reload`: recarga automática al guardar ficheros (solo desarrollo).
- `--workers N`: múltiples workers para producción (requiere Gunicorn).

## Dependencias (Dependency Injection)

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def list_users(db=Depends(get_db)):
    return db.query(User).all()
```

## Buenas practicas

1. Usar modelos Pydantic para entrada y salida, nunca `dict` directos.
2. Manejar todas las excepciones con handlers globales para garantizar respuestas estructuradas.
3. Separar la lógica de negocio del endpoint en servicios o motores externos.
4. Incluir `request_id` en la respuesta para trazabilidad.
5. No bloquear el event loop: usar `async def` para I/O y `def` para CPU-bound con thread pool.
