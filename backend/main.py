import os
import time
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="TorresMack Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Modelos de entrada / salida
# ──────────────────────────────────────────────

class Options(BaseModel):
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 256

class PredictRequest(BaseModel):
    input: str
    history: Optional[list] = []
    options: Optional[Options] = Options()

class PredictResponse(BaseModel):
    ok: bool
    output: Optional[str] = None
    meta: Optional[dict] = None
    error: Optional[dict] = None


# ──────────────────────────────────────────────
# Provider mock (mientras Azure no está listo)
# ──────────────────────────────────────────────

MOCK_RESPONSES = {
    "coche": (
        "El seguro de coche de TorresMack cubre daños propios, responsabilidad civil "
        "frente a terceros y asistencia en carretera 24h. En caso de accidente, llama "
        "al teléfono de asistencia e indica tu número de póliza."
    ),
    "hogar": (
        "El seguro de hogar cubre daños por agua, incendio, robo y responsabilidad civil. "
        "Si tienes un siniestro, haz fotos del daño, no repares nada antes de que lo vea "
        "el perito, y contacta con TorresMack para abrir el parte."
    ),
    "teatro": (
        "Para compañías de teatro ofrecemos pólizas de responsabilidad civil para espectáculos "
        "que cubren accidentes de artistas y técnicos, daños a espectadores y daños al "
        "material escénico durante el transporte. Válida para giras y festivales."
    ),
    "artes": (
        "TorresMack es especialista en seguros para artes escénicas. Cubrimos festivales, "
        "giras, obras puntuales y compañías estables. Escríbenos a info@torresmack.com "
        "para un presupuesto personalizado."
    ),
    "precio": (
        "Para darte un presupuesto personalizado necesitamos más información sobre tu caso. "
        "Por favor contacta con nuestro equipo en info@torresmack.com o llámanos al "
        "teléfono de atención al cliente."
    ),
    "contratar": (
        "Para contratar una póliza, contacta con nuestro equipo en info@torresmack.com "
        "o llámanos directamente. Estaremos encantados de asesorarte."
    ),
}

DEFAULT_MOCK = (
    "Hola, soy el asistente de TorresMack Correduría de Seguros. Puedo ayudarte con "
    "información sobre seguros de coche, hogar y artes escénicas. ¿En qué puedo ayudarte?"
)

def mock_provider(user_input: str) -> str:
    """Devuelve una respuesta simulada basada en palabras clave."""
    text = user_input.lower()
    for keyword, response in MOCK_RESPONSES.items():
        if keyword in text:
            return response
    return DEFAULT_MOCK


# ──────────────────────────────────────────────
# Provider Azure (TODO: conectar cuando esté listo)
# ──────────────────────────────────────────────

def azure_provider(user_input: str, history: list, options: Options) -> str:
    """
    TODO: conectar Azure OpenAI cuando estén disponibles las credenciales.

    Necesita:
    - AZURE_OPENAI_ENDPOINT  → URL del recurso en Azure
    - AZURE_OPENAI_KEY       → clave de API
    - AZURE_DEPLOYMENT_NAME  → nombre del deployment (ej: gpt-4o)

    Comando de prueba:
    curl -X POST http://localhost:8000/predict \
      -H "Content-Type: application/json" \
      -d '{"input": "¿Qué cubre el seguro de hogar?"}'
    """
    raise NotImplementedError("Azure no está configurado todavía.")


# ──────────────────────────────────────────────
# Endpoint principal
# ──────────────────────────────────────────────

USE_MOCK = not bool(os.getenv("AZURE_OPENAI_KEY"))

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if not req.input or not req.input.strip():
        return PredictResponse(
            ok=False,
            error={
                "code": "INVALID_INPUT",
                "message": "El mensaje no puede estar vacío.",
                "details": {"field": "input"}
            }
        )

    start = time.time()

    try:
        if USE_MOCK:
            output = mock_provider(req.input)
            model_used = "mock"
        else:
            output = azure_provider(req.input, req.history, req.options)
            model_used = os.getenv("AZURE_DEPLOYMENT_NAME", "unknown")

        latency_ms = int((time.time() - start) * 1000)

        return PredictResponse(
            ok=True,
            output=output,
            meta={
                "model": model_used,
                "latency_ms": latency_ms,
                "mock": USE_MOCK,
            }
        )

    except Exception as e:
        return PredictResponse(
            ok=False,
            error={
                "code": "INTERNAL_ERROR",
                "message": "Ha ocurrido un error procesando tu consulta. Inténtalo de nuevo.",
                "details": {"exception": str(e)}
            }
        )


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": USE_MOCK}
