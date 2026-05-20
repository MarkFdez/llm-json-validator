# Python para APIs Web

Python es uno de los lenguajes más populares para construir APIs web gracias a su ecosistema maduro, legibilidad y velocidad de desarrollo.

## Frameworks principales

| Framework  | Tipo   | Puntos fuertes                          |
|------------|--------|-----------------------------------------|
| FastAPI    | ASGI   | Rendimiento, tipado, documentacion auto |
| Flask      | WSGI   | Sencillez, flexibilidad, ecosystem      |
| Django REST| WSGI   | Batteries-included, admin, ORM          |
| Starlette  | ASGI   | Base de FastAPI, muy ligero             |
| Litestar   | ASGI   | Alternativa moderna a FastAPI           |

## Buenas practicas en Python para APIs

### 1. Tipado estatico

```python
from typing import Optional, List

def process(items: List[str], limit: Optional[int] = None) -> dict:
    ...
```

Usar `mypy` o `pyright` para verificacion estatica.

### 2. Gestion de dependencias

```bash
pip install -r requirements.txt   # instalar
pip freeze > requirements.txt     # guardar versiones exactas
```

Preferir `pyproject.toml` + `poetry` o `uv` para proyectos modernos.

### 3. Variables de entorno

```python
import os
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")
```

Nunca hardcodear credenciales en el codigo. Usar `.env` + `python-dotenv` en desarrollo.

### 4. Logging estructurado

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("servidor arrancado en puerto %s", 8000)
```

### 5. Manejo de errores

- Nunca exponer tracebacks al cliente en produccion.
- Siempre devolver JSON estructurado incluso en errores.
- Clasificar errores con codigos tipificados.

### 6. Testing

```bash
pytest tests/ -v              # ejecutar tests
pytest --cov=src tests/       # con cobertura
```

### 7. Curl para probar endpoints

```bash
# GET
curl http://localhost:8000/items

# POST con JSON
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "Dame 3 pasos para depurar un error 500"}'

# Con variable de entorno
curl -s http://localhost:8000/predict | python -m json.tool
```

## Paquetes esenciales para APIs

- `fastapi` + `uvicorn[standard]` — servidor ASGI
- `pydantic` — validacion de datos
- `httpx` / `requests` — cliente HTTP
- `pytest` + `httpx` — testing de endpoints
- `python-dotenv` — variables de entorno desde `.env`
- `structlog` — logging estructurado en JSON
