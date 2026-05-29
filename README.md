# TorresMack — Asistente de Seguros 🎭

Chatbot de atención al cliente para TorresMack Correduría de Seguros.  
Responde dudas sobre seguros de **coche**, **hogar** y **artes escénicas**.

> Práctica 12 · Guillermo Torres Lamas (G5)

---

## Estructura del proyecto

```
torresmack-chatbot/
├── backend/
│   ├── main.py              # API FastAPI con POST /predict
│   ├── requirements.txt
│   ├── .env.example         # Plantilla de variables de entorno
│   └── logs.jsonl           # Registro de llamadas al modelo
├── ui/
│   ├── app.py               # Interfaz Gradio
│   └── requirements.txt
├── tests/
│   └── smoke.jsonl          # Casos de prueba básicos
├── data/
│   └── .gitkeep
├── .gitignore
└── README.md
```

---

## Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/GuilermoT/torresmack-chatbot.git
cd torresmack-chatbot
```

### 2. Instala dependencias del backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Instala dependencias de la UI

```bash
cd ../ui
pip install -r requirements.txt
```

### 4. Configura las variables de entorno

```bash
cp backend/.env.example backend/.env
# Edita backend/.env con tus credenciales
```

---

## Variables de entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `LLM_PROVIDER` | `mock` o `foundry` (usa mock si está vacía) | No |
| `AZURE_OPENAI_ENDPOINT` | URL del recurso Azure AI Foundry | Solo con foundry |
| `AZURE_OPENAI_BASE_URL` | URL base para las llamadas al modelo | Solo con foundry |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Nombre del deployment (`DeepSeek-V4-Flash`) | Solo con foundry |
| `AZURE_OPENAI_API_KEY` | Clave de API de Azure | Solo con foundry |
| `GROUP_ID` | Identificador del grupo (G1..G6) | No (default G1) |

> ⚠️ Nunca subas el `.env` al repositorio — está excluido en `.gitignore`

---

## Ejecución

### Lanzar el backend (terminal 1)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Disponible en: http://localhost:8000  
Documentación: http://localhost:8000/docs

### Lanzar la UI (terminal 2)

```bash
cd ui
python app.py
```

Disponible en: http://localhost:7860

---

## Contrato de la API

### POST /predict

**Request:**
```json
{
  "input": "¿Qué cubre el seguro de hogar?",
  "history": [],
  "options": {
    "temperature": 0.2,
    "max_tokens": 600
  }
}
```

**Response OK:**
```json
{
  "ok": true,
  "output": "El seguro de hogar cubre daños por agua, incendio...",
  "meta": {
    "provider": "foundry",
    "deployment": "DeepSeek-V4-Flash",
    "latency_ms": 3686,
    "prompt_tokens": 104,
    "completion_tokens": 140,
    "total_tokens": 244,
    "request_id": "uuid..."
  }
}
```

**Response ERROR:**
```json
{
  "ok": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "El mensaje no puede estar vacío.",
    "details": {
      "field": "input"
    }
  }
}
```

### GET /health

```json
{ "status": "ok", "provider": "foundry", "deployment": "DeepSeek-V4-Flash" }
```

---

## Logs

Cada llamada al modelo se registra automáticamente en `backend/logs.jsonl`.

**Formato de cada entrada:**
```json
{
  "ts": "2026-05-29T17:45:20+0200",
  "group_id": "G5",
  "exercise_id": "P12-S2",
  "request_id": "uuid...",
  "deployment": "DeepSeek-V4-Flash",
  "prompt_tokens": 104,
  "completion_tokens": 140,
  "total_tokens": 244,
  "latency_ms": 3686
}
```

**Ver los logs:**
```bash
# Windows
Get-Content backend/logs.jsonl

# Mac/Linux
cat backend/logs.jsonl
```

---

## Casos de prueba (smoke.jsonl)

| # | Input | Tipo esperado | Output obtenido |
|---|-------|--------------|-----------------|
| 1 | ¿Qué cubre el seguro a todo riesgo? | Resolver | Daños propios, RC, robo, incendio, asistencia en carretera |
| 2 | Se me ha roto una tubería, ¿qué hago? | Resolver | Pasos: cortar agua, documentar, contactar TorresMack |
| 3 | ¿Qué seguro necesita una compañía de teatro para una gira? | Resolver | RC espectáculos, accidentes, material escénico, cobertura gira |
| 4 | Quiero contratar una póliza, ¿cuánto cuesta? | Derivar | Deriva a info@torresmack.com |
| 5 | (mensaje vacío) | Error | INVALID_INPUT |