# app.py
#
# INTERFAZ DE USUARIO (Gradio) — capa cliente.
# Responsabilidades:
#   1. Mostrar un formulario al usuario
#   2. Hacer POST a /predict con el texto introducido
#   3. Mostrar la respuesta JSON, si pasó la validación y la latencia
#   4. Manejar errores de red o del servidor de forma visible
#
# Esta capa NO sabe nada del modelo ni del motor:
# solo conoce la URL del endpoint y el contrato JSON.
# -----------------------------------------------------------------------

import time

import gradio as gr
import json
import requests

API_URL = "http://127.0.0.1:8000/predict"
TIMEOUT_SECONDS = 180


def call_api(text: str):
    if not text or not text.strip():
        return "⚠️ Escribe algo antes de enviar.", "", ""

    payload = {"input": text.strip()}

    try:
        t0 = time.time()
        r = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
        latency_ms = int((time.time() - t0) * 1000)
        r.raise_for_status()
        data = r.json()  # {"ok": bool, "data": {"answer": ..., "confidence": ..., ...}}

        output_pretty = json.dumps(data, ensure_ascii=False, indent=2)

        if data.get("ok"):
            estado = "✅ ok=true — JSON válido"
        else:
            err = data.get("data", {}).get("error", "?")
            estado = f"❌ ok=false — {err}"

        info = f"Latencia: {latency_ms} ms"

        return output_pretty, estado, info

    except requests.exceptions.ConnectionError:
        return (
            "❌ No se pudo conectar al servidor.\n"
            "Asegúrate de que uvicorn está corriendo en el puerto 8000.",
            "", ""
        )
    except requests.exceptions.Timeout:
        return (
            f"⏱️ Timeout: el servidor no respondió en {TIMEOUT_SECONDS} s.",
            "", ""
        )
    except requests.exceptions.HTTPError as e:
        return f"❌ Error del servidor: {e}\nRespuesta: {r.text}", "", ""
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}", "", ""


# ── Interfaz Gradio ───────────────────────────────────────────────────

with gr.Blocks(title="Cliente /predict — JSON Validator") as demo:
    gr.Markdown(
        """
        # 🤖 Cliente del Servicio de Inferencia
        Envía texto al endpoint `POST /predict` y visualiza la respuesta JSON del modelo y su validación.
        """
    )

    with gr.Row():
        input_box = gr.Textbox(
            label="Entrada",
            placeholder="Escribe tu pregunta aquí...",
            lines=3,
        )

    with gr.Row():
        submit_btn = gr.Button("Enviar ▶", variant="primary")
        clear_btn  = gr.Button("Limpiar 🗑️")

    output_box = gr.Textbox(label="JSON devuelto por el modelo", lines=10, interactive=False)
    valid_box  = gr.Textbox(label="Validación", interactive=False)
    meta_box   = gr.Textbox(label="Info (latencia)", interactive=False)

    submit_btn.click(
        fn=call_api,
        inputs=input_box,
        outputs=[output_box, valid_box, meta_box],
    )

    clear_btn.click(
        fn=lambda: ("", "", ""),
        inputs=None,
        outputs=[output_box, valid_box, meta_box],
    )

    input_box.submit(
        fn=call_api,
        inputs=input_box,
        outputs=[output_box, valid_box, meta_box],
    )

    gr.Markdown(
        """
        ---
        **Prueba error 422:** abre otra terminal y ejecuta:
        ```bash
        curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{}'
        ```
        Deberías recibir `422 Unprocessable Entity` porque falta el campo `input`.
        """
    )


if __name__ == "__main__":
    demo.launch(share=False)
