# run_eval.py
#
# Runner de evaluacion automatizada del endpoint POST /predict.
# Lee casos de eval/cases.jsonl, llama al servidor, valida cada respuesta
# y genera un resumen en consola + eval_results.json.
#
# Uso:
#   python run_eval.py                          # baseline, 50 casos
#   python run_eval.py --mode rag               # con RAG activo en el servidor
#   python run_eval.py --cases eval/cases.jsonl --out eval_results.json
#   python run_eval.py --url http://127.0.0.1:8000/predict
#
# Requiere: servidor activo en el puerto indicado.
# ─────────────────────────────────────────────────────────────────────────────

import argparse
import json
import sys
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

from validator import validate_output

# Forzar UTF-8 en stdout para evitar errores de encoding en Windows (cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_API_URL  = "http://127.0.0.1:8000/predict"
DEFAULT_CASES    = "eval/cases.jsonl"
DEFAULT_OUT      = "eval_results.json"
TIMEOUT_S        = 180


# ── I/O ───────────────────────────────────────────────────────────────────────

def load_cases(path: str) -> List[Dict[str, Any]]:
    """Carga casos desde un fichero JSONL (una línea = un caso)."""
    cases: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"  [WARN] linea {lineno} invalida en {path}: {exc}", file=sys.stderr)
    return cases


# ── Llamada al endpoint ────────────────────────────────────────────────────────

def call_predict(user_input: str, api_url: str) -> Dict[str, Any]:
    """
    Llama a POST /predict y devuelve un dict con:
      raw_text   : cuerpo de la respuesta HTTP (string)
      latency_ms : tiempo de respuesta en ms
      http_ok    : True si status_code == 200
      exception  : 'timeout' | 'request_error' | None
    """
    t0 = time.time()
    try:
        resp = requests.post(
            api_url,
            json={"input": user_input},
            timeout=TIMEOUT_S,
        )
        return {
            "raw_text":   resp.text,
            "latency_ms": int((time.time() - t0) * 1000),
            "http_ok":    resp.status_code == 200,
            "exception":  None,
        }
    except requests.Timeout:
        return {
            "raw_text":   "",
            "latency_ms": int((time.time() - t0) * 1000),
            "http_ok":    False,
            "exception":  "timeout",
        }
    except Exception:
        return {
            "raw_text":   "",
            "latency_ms": int((time.time() - t0) * 1000),
            "http_ok":    False,
            "exception":  "request_error",
        }


# ── Evaluación de un caso ─────────────────────────────────────────────────────

def evaluate_case(
    case: Dict[str, Any],
    api_url: str,
) -> Dict[str, Any]:
    """
    Ejecuta un caso y devuelve su resultado completo.
    Siempre retorna un dict; nunca lanza excepción.
    """
    user_input = case.get("input", "")
    http_result = call_predict(user_input, api_url)

    if http_result["exception"]:
        # Sin respuesta HTTP: el servidor no estaba disponible
        ok         = False
        error_type = http_result["exception"]
    else:
        ok, error_type, _ = validate_output(http_result["raw_text"])

    return {
        "id":          case.get("id", "?"),
        "category":    case.get("category", "?"),
        "input":       (user_input[:120] + "...") if len(user_input) > 120 else user_input,
        "pass":        ok,
        "error_type":  error_type,
        "latency_ms":  http_result["latency_ms"],
    }


# ── Reporte en consola ────────────────────────────────────────────────────────

def print_summary(
    results: List[Dict[str, Any]],
    mode: str,
    api_url: str,
) -> None:
    total      = len(results)
    pass_count = sum(1 for r in results if r["pass"])
    fail_count = total - pass_count
    pass_rate  = pass_count / total if total else 0.0
    latencies  = [r["latency_ms"] for r in results]
    avg_lat    = sum(latencies) / len(latencies) if latencies else 0.0

    errors = Counter(
        r["error_type"]
        for r in results
        if not r["pass"] and r["error_type"]
    )

    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  RESUMEN  |  modo: {mode}  |  endpoint: {api_url}")
    print(sep)
    print(f"  total          : {total}")
    print(f"  pass           : {pass_count}")
    print(f"  fail           : {fail_count}")
    print(f"  pass_rate      : {pass_rate:.1%}")
    print(f"  avg_latency_ms : {avg_lat:.0f} ms")

    if errors:
        print(f"\n  Top errores frecuentes:")
        for err, count in errors.most_common(3):
            print(f"    {count:>3}x  {err}")

    print(sep)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluacion automatizada del endpoint /predict",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode", choices=["baseline", "rag"], default="baseline",
        help="Modo de ejecucion (default: baseline)",
    )
    parser.add_argument(
        "--cases", default=DEFAULT_CASES,
        help=f"Ruta al fichero JSONL de casos (default: {DEFAULT_CASES})",
    )
    parser.add_argument(
        "--out", default=DEFAULT_OUT,
        help=f"Ruta del fichero de resultados (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--url", default=DEFAULT_API_URL,
        help=f"URL del endpoint (default: {DEFAULT_API_URL})",
    )
    args = parser.parse_args()

    # ── Cargar casos ──────────────────────────────────────────────────────────
    try:
        cases = load_cases(args.cases)
    except FileNotFoundError:
        print(f"ERROR: no se encontro el fichero de casos: {args.cases}", file=sys.stderr)
        sys.exit(1)

    print(f"\n  Cargados {len(cases)} casos desde '{args.cases}'")
    print(f"  Modo: {args.mode}  |  Endpoint: {args.url}\n")

    # ── Evaluar ───────────────────────────────────────────────────────────────
    results: List[Dict[str, Any]] = []
    for idx, case in enumerate(cases, 1):
        result = evaluate_case(case, args.url)
        results.append(result)

        status = "PASS" if result["pass"] else f"FAIL ({result['error_type']})"
        print(
            f"  [{result['id']}] {result['category']:<16} "
            f"{status:<35} {result['latency_ms']:>5} ms"
        )

    # ── Resumen en consola ────────────────────────────────────────────────────
    print_summary(results, mode=args.mode, api_url=args.url)

    # ── Guardar eval_results.json ─────────────────────────────────────────────
    total      = len(results)
    pass_count = sum(1 for r in results if r["pass"])
    fail_count = total - pass_count
    pass_rate  = pass_count / total if total else 0.0
    latencies  = [r["latency_ms"] for r in results]
    avg_lat    = sum(latencies) / len(latencies) if latencies else 0.0
    errors     = Counter(
        r["error_type"]
        for r in results
        if not r["pass"] and r["error_type"]
    )

    output = {
        "run_id":    str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode":      args.mode,
        "endpoint":  args.url,
        "summary": {
            "total":          total,
            "pass":           pass_count,
            "fail":           fail_count,
            "pass_rate":      round(pass_rate, 4),
            "avg_latency_ms": round(avg_lat, 1),
            "top_errors": [
                {"error_type": err, "count": cnt}
                for err, cnt in errors.most_common(3)
            ],
        },
        "cases": results,
    }

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)

    print(f"\n  Resultados guardados en: {args.out}\n")


if __name__ == "__main__":
    main()
