# Depuracion de APIs

## Error 500 — Internal Server Error

Un error 500 indica que algo fallo inesperadamente en el servidor. Pasos para depurarlo:

1. **Revisar los logs del servidor**: el traceback completo suele estar en la consola o en el fichero de log. Buscar la linea `Traceback (most recent call last)` y leer el error final.
2. **Reproducir con curl**: aislar el problema con la peticion minima que lo provoca:
   ```bash
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"input": "test"}' -v
   ```
3. **Activar modo debug**: en FastAPI, `uvicorn server:app --reload`. En Django, `DEBUG=True`.
4. **Verificar dependencias externas**: si el servidor llama a otro servicio (Ollama, base de datos), comprobar que estan arrancados y accesibles.
5. **Revisar variables de entorno**: una variable de entorno faltante puede causar `None` donde se espera un string.

## Error 422 — Unprocessable Entity

FastAPI devuelve 422 cuando el body de la peticion no cumple el schema Pydantic.

```json
{
  "detail": [
    {
      "loc": ["body", "input"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

Causa habitual: enviar `{}` en lugar de `{"input": "texto"}`.

## Error 404 — Not Found

- La ruta no existe en el servidor.
- Comprobar que la URL es correcta: `POST /predict`, no `GET /predict` ni `/Predict`.
- En FastAPI, `/docs` lista todos los endpoints disponibles.

## Error 401/403

- 401: falta token de autenticacion.
- 403: token valido pero sin permiso para ese recurso.

## Herramientas de depuracion

### curl con verbosidad

```bash
curl -v http://localhost:8000/predict -X POST \
  -H "Content-Type: application/json" \
  -d '{"input": "hola"}'
```

La salida `-v` muestra cabeceras de peticion y respuesta.

### httpie (alternativa legible a curl)

```bash
http POST localhost:8000/predict input="hola"
```

### Python requests para depurar

```python
import requests
r = requests.post("http://localhost:8000/predict", json={"input": "hola"})
print(r.status_code)
print(r.json())
```

### Revisar el cuerpo completo de la respuesta de error

Los servidores bien diseñados devuelven JSON estructurado incluso en errores:

```json
{
  "ok": false,
  "data": {
    "answer": "",
    "confidence": 0,
    "actions": [],
    "error": "engine_unavailable"
  }
}
```

## Lista de comprobacion para un 500

- [ ] Logs del servidor revisados
- [ ] Dependencias externas accesibles (Ollama, DB, etc.)
- [ ] Variables de entorno configuradas
- [ ] Peticion reproducida con curl
- [ ] Timeout suficiente (modelos LLM pueden tardar 30-120 s)
- [ ] El error esta controlado y no expone traceback al cliente
