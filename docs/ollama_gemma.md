# Ollama y Gemma 3

## Que es Ollama

Ollama es una herramienta de linea de comandos que permite ejecutar modelos de lenguaje (LLMs) en local, sin necesidad de GPU en la nube. Gestiona la descarga, cuantizacion y servicio de modelos como Gemma, Llama, Mistral, etc.

## Instalacion y uso basico

```bash
# Instalar (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Descargar y ejecutar un modelo
ollama run gemma3:latest

# Solo descargar
ollama pull gemma3:latest

# Listar modelos instalados
ollama list

# Ver estado del servicio
ollama ps
```

## API REST de Ollama

Ollama expone una API HTTP en `http://127.0.0.1:11434`.

### Endpoint de generacion

```
POST http://127.0.0.1:11434/api/generate
```

**Body:**
```json
{
  "model": "gemma3:latest",
  "prompt": "Tu prompt aqui",
  "stream": false,
  "options": {
    "temperature": 0.1,
    "num_predict": 1024
  }
}
```

**Respuesta:**
```json
{
  "model": "gemma3:latest",
  "created_at": "2024-01-01T00:00:00Z",
  "response": "texto generado por el modelo",
  "done": true,
  "total_duration": 1234567890
}
```

### Parametros de opciones relevantes

| Parametro     | Descripcion                                          | Valor recomendado para JSON |
|---------------|------------------------------------------------------|-----------------------------|
| `temperature` | Aleatoriedad (0=deterministico, 2=muy creativo)      | 0.1 (muy bajo para JSON)    |
| `num_predict` | Maximo de tokens a generar                           | 1024                        |
| `top_p`       | Nucleus sampling                                     | 0.9                         |
| `top_k`       | Top-K sampling                                       | 40                          |

## Gemma 3

Gemma 3 es la familia de modelos de lenguaje abiertos de Google. Disponible en variantes 1B, 4B, 12B y 27B parametros.

### Caracteristicas

- Entrenado con instruction tuning para seguir instrucciones.
- Buen rendimiento en tareas de generacion estructurada (JSON) con temperatura baja.
- Soporta multilingue incluido espanol.

### Prompt engineering para JSON estricto

Para que Gemma 3 genere JSON fiable:

1. Indicar explicitamente "devuelve SOLO JSON, sin texto antes ni despues".
2. Usar temperatura muy baja (0.1).
3. Proporcionar el schema exacto en el prompt.
4. Incluir reglas de coherencia logica explicitas.
5. Indicar tipos de datos con ejemplos: `"confidence": 0.85 <- numero decimal, NO string`.

### Ejemplo de llamada en Python

```python
import requests

response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gemma3:latest",
        "prompt": "Devuelve JSON: {\"ok\": true, \"data\": {\"answer\": \"hola\"}}",
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 512}
    },
    timeout=120
)
response.raise_for_status()
result = response.json()["response"].strip()
```

## Errores comunes con Ollama

- **ConnectionError**: Ollama no esta arrancado. Ejecutar `ollama serve` o reinstalar.
- **404 model not found**: el modelo no esta descargado. Ejecutar `ollama pull gemma3:latest`.
- **Timeout**: el modelo tarda demasiado. Aumentar el timeout o usar un modelo mas pequeno.
- **Out of memory**: el modelo no cabe en RAM. Usar version cuantizada (`gemma3:2b`).
