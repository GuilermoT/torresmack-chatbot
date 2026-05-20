import gradio as gr
import requests
import json

BACKEND_URL = "http://localhost:8000/predict"

# ──────────────────────────────────────────────
# Lógica de llamada al backend
# ──────────────────────────────────────────────

def chat(user_message: str, history: list):
    """Envía el mensaje al backend y devuelve la respuesta."""

    if not user_message.strip():
        return history, "", "⚠️ Escribe un mensaje antes de enviar."

    # Formatear historial para el backend
    formatted_history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": msg}
        for i, (msg, _) in enumerate(history)
        for msg in [msg[0], msg[1]]
        if msg
    ]

    payload = {
        "input": user_message,
        "history": formatted_history,
        "options": {"temperature": 0.2, "max_tokens": 256}
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        data = response.json()

        if data.get("ok"):
            bot_reply = data["output"]
            model_info = data.get("meta", {})
            mock_tag = " *(mock)*" if model_info.get("mock") else ""
            bot_reply_display = f"{bot_reply}{mock_tag}"
            error_msg = ""
        else:
            error = data.get("error", {})
            bot_reply_display = f"Lo siento, no he podido procesar tu consulta."
            error_msg = f"❌ {error.get('message', 'Error desconocido')} [{error.get('code', '')}]"

    except requests.exceptions.ConnectionError:
        bot_reply_display = ""
        error_msg = "❌ No se puede conectar con el servidor. ¿Está el backend en marcha?"
    except Exception as e:
        bot_reply_display = ""
        error_msg = f"❌ Error inesperado: {str(e)}"

    history.append((user_message, bot_reply_display))
    return history, "", error_msg


# ──────────────────────────────────────────────
# Interfaz Gradio
# ──────────────────────────────────────────────

with gr.Blocks(
    title="TorresMack — Asistente de Seguros",
    theme=gr.themes.Soft(primary_hue="orange"),
    css="""
        .header { text-align: center; padding: 16px 0 8px 0; }
        .header h1 { font-size: 1.6em; color: #2D2D2D; margin: 0; }
        .header p  { color: #888; margin: 4px 0 0 0; font-size: 0.9em; }
        .error-box { color: #c0392b; font-size: 0.88em; min-height: 24px; }
        footer { display: none !important; }
    """
) as demo:

    # Cabecera
    with gr.Row(elem_classes="header"):
        gr.HTML("""
            <div class="header">
                <h1>🎭 TorresMack · Asistente de Seguros</h1>
                <p>Consulta sobre seguros de coche, hogar y artes escénicas</p>
            </div>
        """)

    # Chat
    chatbot = gr.Chatbot(
        label="Conversación",
        height=420,
        bubble_full_width=False,
        avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=torresmack"),
    )

    # Input
    with gr.Row():
        txt_input = gr.Textbox(
            placeholder="Escribe tu consulta aquí... (ej: ¿Qué cubre el seguro de hogar?)",
            show_label=False,
            scale=5,
            lines=1,
        )
        btn_send = gr.Button("Enviar", variant="primary", scale=1)

    # Área de errores
    txt_error = gr.Markdown(value="", elem_classes="error-box")

    # Ejemplos de consultas
    gr.Examples(
        examples=[
            ["¿Qué cubre el seguro a todo riesgo?"],
            ["Se me ha roto una tubería, ¿qué hago?"],
            ["¿Qué seguro necesita una compañía de teatro para una gira?"],
            ["Quiero contratar una póliza, ¿cuánto cuesta?"],
        ],
        inputs=txt_input,
        label="Ejemplos de consultas",
    )

    # Estado
    state_history = gr.State([])

    # Eventos
    btn_send.click(
        fn=chat,
        inputs=[txt_input, state_history],
        outputs=[chatbot, txt_input, txt_error],
    )
    txt_input.submit(
        fn=chat,
        inputs=[txt_input, state_history],
        outputs=[chatbot, txt_input, txt_error],
    )

    # Actualizar estado interno con el historial del chatbot
    chatbot.change(fn=lambda h: h, inputs=[chatbot], outputs=[state_history])


if __name__ == "__main__":
    demo.launch(server_port=7860, share=False)
