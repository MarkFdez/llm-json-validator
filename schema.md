# Schema JSON — Práctica 10

## Formato objetivo

El modelo debe devolver **exclusivamente** un JSON válido con esta estructura:

```json
{
  "ok": true,
  "data": {
    "answer": "string",
    "confidence": 0.0,
    "actions": ["string"],
    "error": null
  }
}
```

## Campos y tipos

| Campo            | Tipo             | Obligatorio | Descripción                                          |
|------------------|------------------|-------------|------------------------------------------------------|
| `ok`             | `boolean`        | Sí          | `true` si la respuesta es válida, `false` si no      |
| `data`           | `object`         | Sí          | Contenedor de la respuesta                           |
| `data.answer`    | `string`         | Sí          | Respuesta del modelo. Puede ser `""` si hay error    |
| `data.confidence`| `number` (0..1)  | Sí          | Nivel de confianza de la respuesta entre 0 y 1       |
| `data.actions`   | `array[string]`  | Sí          | Lista de acciones sugeridas. Puede estar vacía `[]`  |
| `data.error`     | `string \| null` | Sí          | `null` si ok=true, o mensaje de error si ok=false    |

## Reglas

- `ok` es `true` solo si `data` es válido y completo.
- `confidence` debe estar entre `0` y `1` (inclusive).
- `actions` es una lista de strings (puede ser lista vacía `[]`).
- Si el modelo no puede responder: `answer=""`, `confidence=0`, `actions=[]`, `error="motivo"`.
- **No añadir texto antes ni después del JSON.**

## Ejemplo válido — respuesta correcta

```json
{
  "ok": true,
  "data": {
    "answer": "Para depurar un error 500 revisa los logs del servidor, verifica la configuración y prueba el endpoint con curl.",
    "confidence": 0.85,
    "actions": ["revisar logs", "verificar configuración", "probar con curl"],
    "error": null
  }
}
```

## Ejemplo válido — respuesta de error

```json
{
  "ok": false,
  "data": {
    "answer": "",
    "confidence": 0,
    "actions": [],
    "error": "No puedo proporcionar esa información por razones de seguridad."
  }
}
```
