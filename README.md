# llm-json-validator

Sistema de inferencia con LLM local (Gemma via Ollama) que garantiza respuestas en JSON estructurado y validado. Incluye validador de schema estricto, servidor FastAPI, modulo RAG con TF-IDF y suite de evaluacion automatizada de 50 casos.

---

## Arquitectura

```
app.py (Gradio UI)           run_eval.py (evaluador CLI)
        |                             |
        +----------POST /predict------+
                       |
                 server.py (FastAPI)
                       |
               engine_gemma.py
               /              \
       predict()              RAG (opcional)
           |                  rag/chunker.py
     Ollama API               rag/retriever.py
           |                  docs/*.md
      gemma3:latest
           |
      validator.py
```

**Contrato congelado** (NUNCA modificar):
- Ruta: `POST /predict`
- Body entrada: `{"input": "texto"}`
- Schema de salida: `{"ok": bool, "data": {"answer": str, "confidence": float (0-1), "actions": [str], "error": str|null}}`

---

## Requisitos

- Python 3.10+
- [Ollama](https://ollama.com/) instalado y en ejecucion
- Modelo descargado (recomendado: `gemma3:latest`, ~3.3 GB)

---

## Cold-start en menos de 10 minutos

### Paso 1 — Clonar e instalar dependencias (2 min)

```bash
git clone <url-del-repo>
cd prompting-json2

pip install -r requirements.txt
```

### Paso 2 — Arrancar Ollama y descargar el modelo (5 min)

```bash
# Verificar que Ollama esta corriendo
curl http://127.0.0.1:11434/api/tags

# Si no responde, arrancarlo:
ollama serve          # Linux/macOS (background: ollama serve &)
# En Windows: iniciar desde la bandeja del sistema

# Descargar el modelo (solo la primera vez, ~3.3 GB)
ollama pull gemma3:latest
```

> Alternativa rapida (modelo mas ligero, ~1.6 GB): `ollama pull gemma2:2b`
> Para usarlo: `MODEL_NAME=gemma2:2b uvicorn server:app ...`

### Paso 3 — Arrancar el servidor (30 seg)

```bash
# Terminal 1
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Verificar que esta activo:
```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/hola_mundo
```

### Paso 4 — Hacer una prediccion (10 seg)

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "Dame 3 pasos para depurar un error 500 en una API."}'
```

Respuesta esperada:
```json
{
  "ok": true,
  "data": {
    "answer": "1. Revisar logs del servidor. 2. Reproducir con curl. 3. Aislar el componente fallido.",
    "confidence": 0.9,
    "actions": ["Revisar logs", "Reproducir con curl", "Aislar componente"],
    "error": null
  }
}
```

### Paso 5 — Ejecutar la suite de evaluacion (2 min)

```bash
# Terminal 2 (con el servidor activo en Terminal 1)
python run_eval.py --mode baseline
```

Genera `eval_results.json` con resultados de 50 casos.

> **Nota sobre ficheros de resultados prealmacenados:**
> - `eval_results.json` — ultimo run guardado (puede ser de una sesion anterior; regenera con el comando de arriba).
> - `eval_baseline_10.json` — 10 casos obligatorios en modo baseline con `gemma2:2b`.
> - `eval_rag_50.json` — 50 casos en modo RAG con `gemma2:2b`.
> - Ver `evidencia.md` para la tabla completa de 20 ejecuciones reales (baseline vs RAG).

---

## Variables de entorno

| Variable      | Valores            | Default         | Descripcion                                  |
|---------------|--------------------|-----------------|----------------------------------------------|
| `MODEL_NAME`  | nombre del modelo  | `gemma3:latest` | Modelo Ollama a usar                         |
| `RAG_ENABLED` | `true` / `false`   | `false`         | Activar recuperacion de contexto desde docs/ |
| `MODE`        | `dev` / `prod`     | `dev`           | Nivel de logging (DEBUG vs INFO)             |

---

## Modo RAG

El modulo RAG recupera fragmentos relevantes de los documentos en `docs/` y los inyecta como contexto en el prompt antes de llamar al modelo.

**Activar RAG:**

```bash
# Linux/macOS
RAG_ENABLED=true uvicorn server:app --host 127.0.0.1 --port 8000

# Windows PowerShell
$env:RAG_ENABLED="true"; uvicorn server:app --host 127.0.0.1 --port 8000

# Evaluar con RAG
python run_eval.py --mode rag
```

**Documentos indexados** (`docs/`):

| Fichero               | Contenido                                      |
|-----------------------|------------------------------------------------|
| `api_rest.md`         | Verbos HTTP, codigos de estado, diseno de URLs |
| `docker.md`           | Contenedores, Dockerfile, Docker Compose       |
| `fastapi.md`          | Modelos Pydantic, exception handlers           |
| `python_apis.md`      | Frameworks Python, buenas practicas            |
| `json_schema.md`      | Tipos JSON, errores comunes con LLMs           |
| `ollama_gemma.md`     | API de Ollama, parametros, prompt engineering  |
| `debugging_api.md`    | Depuracion de errores 500/422/404              |
| `deployment_local.md` | Despliegue en local, variables de entorno      |

---

## Suite de evaluacion

```bash
python run_eval.py [opciones]

Opciones:
  --mode baseline|rag       Modo de ejecucion (default: baseline)
  --cases eval/cases.jsonl  Fichero JSONL de casos (default: eval/cases.jsonl)
  --out eval_results.json   Fichero de resultados (default: eval_results.json)
  --url http://...          URL del endpoint (default: http://127.0.0.1:8000/predict)
```

**50 casos en 5 categorias:**

| Categoria        | Casos       | Que prueba                                       |
|------------------|-------------|--------------------------------------------------|
| `mandatory`      | TC-001..010 | Los 10 inputs obligatorios del enunciado         |
| `happy_path`     | TC-011..020 | Preguntas tecnicas normales (API, Docker, Python)|
| `edge_boundary`  | TC-021..030 | Inputs vacios, unicode, saltos de linea, etc.    |
| `type_range`     | TC-031..040 | Confidence extremos, listas largas, respuestas cortas |
| `injection_attack`| TC-041..050 | Inyecciones de prompt, peticiones de ignorar schema |

---

## Estructura del proyecto

```
prompting-json2/
  server.py           # Servidor FastAPI (contrato congelado)
  engine_gemma.py     # Motor de inferencia + soporte RAG
  validator.py        # Validador del schema JSON de salida
  run_eval.py         # Runner de evaluacion automatizada
  app.py              # UI Gradio (opcional)
  docs/               # Documentos de referencia para RAG
    api_rest.md
    docker.md
    fastapi.md
    python_apis.md
    json_schema.md
    ollama_gemma.md
    debugging_api.md
    deployment_local.md
  rag/
    __init__.py
    chunker.py        # chunk_documents(docs, chunk_size=300, overlap=50)
    retriever.py      # retrieve(query, chunks, top_k=3) — TF-IDF + coseno
  eval/
    cases.jsonl       # 50 casos de evaluacion
  eval_results.json   # Resultados de la ultima ejecucion
  errors.md           # Registro de 12 fallos reales y como se resolvieron
  evidencia.md        # Tabla comparativa de 20 ejecuciones (baseline vs RAG)
  schema.md           # Schema JSON objetivo
  prompts.md          # Historial de iteraciones de prompt
  README.md
```

---

## Pruebas rapidas

```bash
# Peticion valida
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "Que es Docker?"}'

# Body sin campo input (debe devolver 422 con schema correcto)
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{}'

# Servidor activo
curl http://127.0.0.1:8000/hola_mundo

# Documentacion interactiva
# Abrir en navegador: http://127.0.0.1:8000/docs
```

---

## Resultados de evaluacion

| Modelo           | Modo     | PASS/Total | pass_rate | avg_latency |
|------------------|----------|------------|-----------|-------------|
| gemma3:1b        | baseline | 1/10       | 10%       | ~500 ms     |
| gemma2:2b        | baseline | 40/50      | 80%       | 621 ms      |
| gemma2:2b + RAG  | rag      | 40/50      | 80%       | 613 ms      |
| gemma3:latest*   | baseline | 50/50      | 100%      | ~8000 ms    |

*Con `gemma3:latest` y prompts del historial en `prompts.md`.

**Modelo recomendado:** `gemma3:latest`
- Equilibrio optimo entre calidad y tamano (~3.3 GB).
- `gemma3:1b` es demasiado pequeno para seguir schemas JSON estrictos.
- `gemma2:2b` funciona pero falla en casos edge con el schema.

---

## Errores frecuentes y soluciones

Ver [errors.md](errors.md) para la tabla completa de 12 fallos documentados.

| Error mas comun              | Causa                              | Solucion                                 |
|------------------------------|------------------------------------|------------------------------------------|
| `json_parse_error`           | Texto antes del JSON o markdown    | Pre-procesado en `validator.py`          |
| `ok_true_but_error_not_null` | Contradiccion logica del modelo    | Regla de coherencia en `validator.py`    |
| `missing_field:error`        | El modelo omite el campo error     | Prompt con campo marcado como obligatorio|
| `engine_unavailable`         | Ollama no esta arrancado           | `ollama serve` antes de arrancar FastAPI |
| `engine_http_error`          | Modelo no descargado               | `ollama pull gemma3:latest`              |
