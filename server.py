# server.py
#
# SERVIDOR FASTAPI — capa intermedia entre la UI y el motor.
# Responsabilidades:
#   1. Exponer el endpoint POST /predict (contrato CONGELADO, no modificar ruta ni schema)
#   2. Validar la entrada vía Pydantic
#   3. Llamar al motor y devolver la respuesta validada
#   4. Garantizar que NINGUNA excepción produce un traceback desnudo al cliente
#
# Regla de oro: el cliente siempre recibe JSON con el schema común, incluso en errores.
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from engine_gemma import predict as engine_predict
from validator import validate_output

app = FastAPI(
    title="Servicio de Inferencia — Gemma 3 + JSON Validator",
    description="API REST para inferencia con Gemma 3. Devuelve JSON validado.",
    version="2.2.0",
)


# ── Helper: respuesta de error estructurada ───────────────────────────────────

def _make_error_response(error_type: str) -> dict:
    """
    Devuelve el schema común con ok=false y el error tipificado.
    Cumple el contrato de salida en cualquier condición de fallo.
    """
    return {
        "ok": False,
        "data": {
            "answer": "",
            "confidence": 0,
            "actions": [],
            "error": error_type,
        },
    }


# ── Manejadores de excepciones globales ──────────────────────────────────────
#
# Garantía: ningún traceback llega al cliente. Toda excepción no controlada
# se transforma en una respuesta JSON con ok=false y el error tipificado.

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    """
    422 Unprocessable Entity — campo 'input' ausente o con tipo incorrecto.
    FastAPI lo lanza antes de que llegue al endpoint; lo capturamos aquí
    para devolver nuestro schema en lugar del formato por defecto de Pydantic.
    """
    details = "; ".join(
        f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in exc.errors()
    )
    return JSONResponse(status_code=422, content=_make_error_response(f"invalid_request: {details}"))


@app.exception_handler(Exception)
async def handle_generic_error(request: Request, exc: Exception):
    """
    500 — red de seguridad para cualquier excepción no controlada en el servidor.
    No debe dispararse nunca en condiciones normales; si lo hace indica un bug
    que hay que investigar en los logs.
    """
    # Deja que FastAPI gestione sus propias HTTPException internas (404, 405…)
    from fastapi import HTTPException as _HTTPExc
    if isinstance(exc, _HTTPExc):
        raise exc
    return JSONResponse(status_code=500, content=_make_error_response(f"internal_error:{type(exc).__name__}"))


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class PredictIn(BaseModel):
    input: str   # obligatorio; ausencia → 422 capturado por handle_validation_error

class PredictData(BaseModel):
    answer: str
    confidence: float
    actions: list[str]
    error: str | None

class PredictOut(BaseModel):
    ok: bool
    data: PredictData


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/predict", response_model=PredictOut)
def predict(body: PredictIn):
    """
    Endpoint principal de inferencia. CONTRATO CONGELADO.

    Recibe:   {"input": "texto del usuario"}
    Devuelve: {"ok": bool, "data": {"answer": str, "confidence": float,
                                    "actions": [str], "error": str|null}}
    """
    # ── Llamada al motor ───────────────────────────────────────────────────────
    try:
        raw_output = engine_predict(body.input)
    except Exception as exc:
        exc_name = type(exc).__name__
        if "ConnectionError" in exc_name:
            error_type = "engine_unavailable"
        elif "Timeout" in exc_name:
            error_type = "engine_timeout"
        elif "HTTPError" in exc_name:
            error_type = "engine_http_error"
        else:
            error_type = f"engine_error:{exc_name}"
        return _make_error_response(error_type)

    # ── Validación de la salida ────────────────────────────────────────────────
    ok, error_type, parsed = validate_output(raw_output)

    if ok and parsed is not None:
        return parsed
    return _make_error_response(error_type or "validation_error")


@app.get("/hola_mundo")
def hola_mundo():
    """Endpoint de prueba — verifica que el servidor está activo."""
    return {"mensaje": "¡El servidor está funcionando correctamente!"}


@app.get("/")
def root():
    return {"info": "Servicio activo. Ve a /docs para la UI interactiva."}
