# TorresMack — Asistente de Seguros 🎭

Chatbot de atención al cliente para TorresMack Correduría de Seguros.  
Responde dudas sobre seguros de **coche**, **hogar** y **artes escénicas**.

> Práctica 12 · Guillermo Torres Lamas

---

## Estructura del proyecto

```
torresmack-chatbot/
├── backend/
│   ├── main.py              # API FastAPI con POST /predict
│   └── requirements.txt
├── ui/
│   ├── app.py               # Interfaz Gradio
│   └── requirements.txt
├── tests/
│   └── smoke.jsonl          # Casos de prueba básicos
├── .env.example             # Variables de entorno (plantilla)
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
cp .env.example .env
# Edita .env con tus credenciales de Azure (opcional, sin ellas usa el mock)
```

---

## Ejecución

### Lanzar el backend (terminal 1)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

El backend estará disponible en: http://localhost:8000  
Documentación automática: http://localhost:8000/docs

### Lanzar la UI (terminal 2)

```bash
cd ui
python app.py
```

La UI estará disponible en: http://localhost:7860

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
    "max_tokens": 256
  }
}
```

**Response OK:**
```json
{
  "ok": true,
  "output": "El seguro de hogar cubre daños por agua, incendio...",
  "meta": {
    "model": "mock",
    "latency_ms": 12,
    "mock": true
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
{ "status": "ok", "mock_mode": true }
```

---

## Prueba rápida (curl)

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "¿Qué cubre el seguro de hogar?"}'
```

---

## Casos de prueba (smoke.jsonl)

| # | Input | Tipo esperado | Tema |
|---|-------|--------------|------|
| 1 | ¿Qué cubre el seguro a todo riesgo? | Resolver | Coche |
| 2 | Se me ha roto una tubería, ¿qué hago? | Resolver | Hogar |
| 3 | ¿Qué seguro necesita una compañía de teatro? | Resolver | Artes |
| 4 | Quiero contratar una póliza, ¿cuánto cuesta? | Derivar | Artes |
| 5 | (mensaje vacío) | Error INVALID_INPUT | Validación |

---

## Variables de entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | URL del recurso Azure OpenAI | No (usa mock si está vacía) |
| `AZURE_OPENAI_KEY` | Clave de API de Azure | No (usa mock si está vacía) |
| `AZURE_DEPLOYMENT_NAME` | Nombre del deployment (ej: gpt-4o) | No |

> Si `AZURE_OPENAI_KEY` está vacía, el backend usa automáticamente el **mock**.

---

## Pendiente para conectar Azure

1. Crear recurso Azure OpenAI en el portal de Azure
2. Crear un deployment con el modelo `gpt-4o`
3. Copiar endpoint y clave en el fichero `.env`
4. Implementar `azure_provider()` en `backend/main.py` usando el SDK de OpenAI
5. Probar con: `curl -X POST http://localhost:8000/predict -d '{"input": "prueba"}'`
