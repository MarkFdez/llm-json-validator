# Despliegue en Local

## Requisitos previos

- Python 3.10 o superior
- pip o uv
- Ollama instalado y arrancado
- Modelo `gemma3:latest` descargado

## Pasos para desplegar en local

### 1. Clonar o descargar el repositorio

```bash
git clone <url-del-repo>
cd proyecto
```

### 2. Crear entorno virtual

```bash
python -m venv .venv

# Activar (Linux/macOS)
source .venv/bin/activate

# Activar (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activar (Windows cmd)
.venv\Scripts\activate.bat
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Arrancar Ollama y descargar el modelo

```bash
ollama serve &            # arrancar en background (Linux/macOS)
ollama pull gemma3:latest # descargar modelo (~1.5 GB)
```

En Windows, iniciar Ollama desde la bandeja del sistema o ejecutar `ollama.exe serve`.

### 5. Arrancar el servidor FastAPI

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

El servidor queda disponible en `http://127.0.0.1:8000`.

Documentacion interactiva: `http://127.0.0.1:8000/docs`.

### 6. Verificar que funciona

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/hola_mundo
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "Dame 3 pasos para depurar un error 500"}'
```

### 7. Ejecutar la suite de evaluacion

```bash
python run_eval.py --mode baseline
```

## Variables de entorno disponibles

| Variable      | Valores        | Descripcion                            |
|---------------|----------------|----------------------------------------|
| `MODE`        | `dev` / `prod` | Nivel de logging (DEBUG vs INFO)       |
| `RAG_ENABLED` | `true`/`false` | Activar modulo RAG (default: false)    |

### Activar RAG

```bash
# Linux/macOS
RAG_ENABLED=true uvicorn server:app --port 8000

# Windows PowerShell
$env:RAG_ENABLED="true"; uvicorn server:app --port 8000

# Evaluar con RAG
python run_eval.py --mode rag
```

## Estructura del proyecto

```
proyecto/
  server.py          # Servidor FastAPI (contrato congelado)
  engine_gemma.py    # Motor de inferencia Ollama
  validator.py       # Validador del schema JSON
  run_eval.py        # Runner de evaluacion automatizada
  app.py             # UI Gradio (opcional)
  docs/              # Documentacion para RAG
  rag/
    chunker.py       # Chunker de documentos
    retriever.py     # Recuperador TF-IDF
  eval/
    cases.jsonl      # 50 casos de evaluacion
  eval_results.json  # Resultados de la ultima ejecucion
```

## Solucion de problemas comunes

**Error: OSError: [Errno 98] Address already in use**
```bash
# Ver que proceso usa el puerto 8000
lsof -i :8000          # Linux/macOS
netstat -ano | findstr 8000  # Windows
# Matar el proceso o usar otro puerto con --port 8001
```

**Error: ConnectionError al llamar a Ollama**
```bash
# Verificar que Ollama esta corriendo
curl http://127.0.0.1:11434/api/tags
# Si no responde, ejecutar: ollama serve
```

**Error de encoding en Windows**
Agregar al inicio del script Python:
```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```
