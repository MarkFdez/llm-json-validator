# validator.py
#
# Validador del schema de salida del modelo.
# Contrato de retorno: (pass: bool, error_type: str | None, parsed_obj: dict | None)
#   - pass=True, error_type=None, parsed_obj=<dict>  → salida válida
#   - pass=False, error_type=<str>, parsed_obj=<dict|None> → fallo con clasificación
#
# Nunca lanza excepción: cualquier entrada produce un resultado tipificado.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
import os
import uuid
from typing import Any, Dict, Optional, Tuple

# ── Logging setup ─────────────────────────────────────────────────────────────
LOGGER = logging.getLogger("validator")
_mode  = os.getenv("MODE", "dev")
_level = logging.DEBUG if _mode == "dev" else logging.INFO
logging.basicConfig(level=_level, format="%(levelname)s  %(message)s")


# ── Utilidades ────────────────────────────────────────────────────────────────

def new_request_id() -> str:
    return str(uuid.uuid4())[:8]


def clip(s: str, n: int = 200) -> str:
    """Recorta un string para los logs; nunca loguear datos completos."""
    s = str(s).replace("\n", " ")
    return s if len(s) <= n else s[:n] + "…"


def try_fix_truncated(raw: str) -> str:
    """
    Cierra un JSON truncado añadiendo los delimitadores que faltan.
    Ejemplo: '{"ok":true,"data":{"answer":"hola"'  →  añade '}}'.
    Solo actúa cuando hay más aperturas que cierres; no modifica JSON bien formado.
    """
    s = raw.strip()
    opens_square = s.count("[") - s.count("]")
    opens_curly  = s.count("{") - s.count("}")
    if opens_square > 0 or opens_curly > 0:
        s += "]" * max(opens_square, 0) + "}" * max(opens_curly, 0)
    return s


# ── Validador principal ───────────────────────────────────────────────────────

def validate_output(
    raw: str,
    request_id: Optional[str] = None,
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Valida la salida cruda del modelo contra el schema contrato.

    Parámetros
    ----------
    raw         : string devuelto por el motor (puede contener bloques markdown,
                  JSON truncado, texto extra, etc.)
    request_id  : ID de traza opcional para los logs.

    Retorna
    -------
    (pass, error_type, parsed_obj)
      pass=True  → salida completamente válida; error_type=None.
      pass=False → fallo; error_type es un código corto como 'json_parse_error',
                   'missing_field:confidence', 'ok_true_but_error_not_null', etc.
    """
    rid = request_id or new_request_id()

    # ── Pre-procesado ─────────────────────────────────────────────────────────
    cleaned = raw.strip()

    # Eliminar bloques ```json ... ``` que el modelo añade a veces
    if cleaned.startswith("```"):
        lines  = cleaned.splitlines()
        lines  = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    # Intentar reparar JSON truncado antes de parsear
    cleaned = try_fix_truncated(cleaned)

    LOGGER.debug("[%s] validando: %s", rid, clip(cleaned, 120))

    # ── 1. JSON parseable ─────────────────────────────────────────────────────
    try:
        obj = json.loads(cleaned)
    except Exception as exc:
        err = "json_parse_error"
        LOGGER.debug("[%s] FAIL parse (%s): %s", rid, exc, clip(cleaned, 80))
        LOGGER.info("[%s] ERROR: %s", rid, err)
        return False, err, None

    if not isinstance(obj, dict):
        err = "not_a_dict"
        LOGGER.info("[%s] ERROR: %s", rid, err)
        return False, err, None

    # ── 2. Campos raíz obligatorios ───────────────────────────────────────────
    if "ok" not in obj:
        LOGGER.info("[%s] ERROR: missing_field:ok", rid)
        return False, "missing_field:ok", obj

    if "data" not in obj:
        LOGGER.info("[%s] ERROR: missing_field:data", rid)
        return False, "missing_field:data", obj

    # ── 3. Tipo de ok ─────────────────────────────────────────────────────────
    if not isinstance(obj["ok"], bool):
        err = "ok_not_bool"
        LOGGER.info("[%s] ERROR: %s (valor=%s)", rid, err, obj["ok"])
        return False, err, obj

    # ── 4. data es un dict ────────────────────────────────────────────────────
    data = obj["data"]
    if not isinstance(data, dict):
        LOGGER.info("[%s] ERROR: data_not_dict", rid)
        return False, "data_not_dict", obj

    # ── 5. Campos obligatorios dentro de data ─────────────────────────────────
    for k in ("answer", "confidence", "actions", "error"):
        if k not in data:
            err = f"missing_field:{k}"
            LOGGER.info("[%s] ERROR: %s", rid, err)
            return False, err, obj

    # ── 6. Tipos de cada campo ────────────────────────────────────────────────
    if not isinstance(data["answer"], str):
        LOGGER.info("[%s] ERROR: answer_not_str", rid)
        return False, "answer_not_str", obj

    conf = data["confidence"]
    if not isinstance(conf, (int, float)) or isinstance(conf, bool):
        err = "confidence_not_number"
        LOGGER.info("[%s] ERROR: %s (valor=%s)", rid, err, conf)
        return False, err, obj

    if not (0.0 <= conf <= 1.0):
        err = "confidence_out_of_range"
        LOGGER.info("[%s] ERROR: %s (valor=%s)", rid, err, conf)
        return False, err, obj

    if not isinstance(data["actions"], list):
        LOGGER.info("[%s] ERROR: actions_not_list", rid)
        return False, "actions_not_list", obj

    if any(not isinstance(x, str) for x in data["actions"]):
        LOGGER.info("[%s] ERROR: actions_has_non_str", rid)
        return False, "actions_has_non_str", obj

    err_field = data["error"]
    if err_field is not None and not isinstance(err_field, str):
        LOGGER.info("[%s] ERROR: error_not_str_or_null", rid)
        return False, "error_not_str_or_null", obj

    # ── 7. Coherencia lógica: ok=true implica error=null ─────────────────────
    if obj["ok"] is True and data["error"] is not None:
        err = "ok_true_but_error_not_null"
        LOGGER.info("[%s] ERROR: %s", rid, err)
        return False, err, obj

    # ── Todo OK ───────────────────────────────────────────────────────────────
    LOGGER.debug("[%s] validación OK", rid)
    LOGGER.info("[%s] OK", rid)
    return True, None, obj


# ── Smoke-test directo ────────────────────────────────────────────────────────
if __name__ == "__main__":
    CASES = [
        (
            '{"ok": true, "data": {"answer": "Hola", "confidence": 0.9, '
            '"actions": ["paso 1"], "error": null}}',
            "caso válido",
        ),
        ('{"ok": true, "data": {', "JSON truncado (auto-repair)"),
        (
            '{"ok": true, "data": {"answer": "Hola", "confidence": 0.9, "actions": []}}',
            "falta campo error",
        ),
        (
            '{"ok": true, "data": {"answer": "Hola", "confidence": 1.5, '
            '"actions": [], "error": null}}',
            "confidence fuera de rango",
        ),
        (
            '```json\n{"ok": true, "data": {"answer": "test", "confidence": 0.8, '
            '"actions": [], "error": null}}\n```',
            "bloque markdown",
        ),
        (
            '{"ok": true, "data": {"answer": "test", "confidence": 0.8, '
            '"actions": [], "error": "algo"}}',
            "ok=true pero error!=null",
        ),
        (
            '{"ok": "true", "data": {"answer": "x", "confidence": 0.5, '
            '"actions": [], "error": null}}',
            "ok como string en lugar de bool",
        ),
        (
            '{"ok": false, "data": {"answer": "", "confidence": 0, '
            '"actions": [1, 2, 3], "error": "motivo"}}',
            "actions con enteros en lugar de strings",
        ),
    ]

    print("-" * 60)
    for i, (raw, desc) in enumerate(CASES, 1):
        ok, err_type, _ = validate_output(raw)
        status = "PASS" if ok else f"FAIL  ({err_type})"
        print(f"  [{i}] {desc:<40}  {status}")
    print("-" * 60)
