# JSON y Esquemas de Datos

## Que es JSON

JSON (JavaScript Object Notation) es un formato de intercambio de datos ligero, legible por humanos y maquinas. Es el estandar de facto para APIs web.

## Sintaxis basica

```json
{
  "string": "texto",
  "numero": 42,
  "decimal": 3.14,
  "booleano": true,
  "nulo": null,
  "array": [1, 2, 3],
  "objeto": {
    "clave": "valor"
  }
}
```

## Reglas de JSON (RFC 8259)

- Las claves deben ser strings entre comillas dobles.
- Los strings usan comillas dobles, nunca simples.
- No se permiten comentarios.
- No se permiten comas finales (trailing commas).
- Los caracteres especiales en strings deben escaparse: `\"`, `\\`, `\n`, `\t`, `\uXXXX`.
- Los numeros no pueden tener ceros iniciales: `01` es invalido.

## Tipos de datos JSON

| Tipo    | Ejemplo              | Python equivalente |
|---------|----------------------|-------------------|
| string  | `"hola"`             | `str`             |
| number  | `42`, `3.14`         | `int`, `float`    |
| boolean | `true`, `false`      | `bool`            |
| null    | `null`               | `None`            |
| array   | `[1, "a", true]`     | `list`            |
| object  | `{"k": "v"}`         | `dict`            |

## JSON Schema

JSON Schema es un vocabulario para validar la estructura de documentos JSON.

```json
{
  "type": "object",
  "required": ["ok", "data"],
  "properties": {
    "ok": {"type": "boolean"},
    "data": {
      "type": "object",
      "required": ["answer", "confidence", "actions", "error"],
      "properties": {
        "answer":     {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "actions":    {"type": "array", "items": {"type": "string"}},
        "error":      {"type": ["string", "null"]}
      }
    }
  }
}
```

## Errores comunes al generar JSON con LLMs

1. **Texto antes del JSON**: el modelo añade prefijos como "Aqui tienes:" antes del `{`.
2. **Bloques markdown**: envuelve el JSON en ` ```json ... ``` `.
3. **JSON truncado**: el modelo para a mitad del objeto por limite de tokens.
4. **Tipos incorrectos**: `"confidence": "0.9"` en lugar de `"confidence": 0.9`.
5. **Campos faltantes**: omite campos opcionales que en realidad son obligatorios.
6. **Coherencia logica**: `"ok": true` con `"error": "mensaje"` es una contradiccion.

## Parsing en Python

```python
import json

# Parsear string a dict
data = json.loads('{"ok": true, "data": {"answer": "Hola"}}')

# Serializar dict a string
text = json.dumps({"ok": True, "data": {"answer": "Hola"}}, ensure_ascii=False)

# Con indentacion (legible)
pretty = json.dumps(data, indent=2, ensure_ascii=False)
```

## Validacion de tipos en Python

```python
obj = json.loads(raw)
assert isinstance(obj, dict), "debe ser un objeto JSON"
assert isinstance(obj["ok"], bool), "ok debe ser boolean"
assert isinstance(obj["data"]["confidence"], (int, float)), "confidence debe ser numero"
assert 0.0 <= obj["data"]["confidence"] <= 1.0, "confidence fuera de rango"
assert isinstance(obj["data"]["actions"], list), "actions debe ser array"
```
