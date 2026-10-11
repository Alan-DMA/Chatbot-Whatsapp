# Plan 001 — Configuración Core y Conexión de Texto

## Arquitectura y archivos afectados
- `requirements.txt`: Dependencias del proyecto (`fastapi`, `uvicorn`, `httpx`, `google-genai` / `google-generativeai`, `python-dotenv`, `pytest`).
- `.env.example`: Plantilla de variables de entorno (`WHATSAPP_TOKEN`, `VERIFY_TOKEN`, `PHONE_NUMBER_ID`, `GEMINI_API_KEY`, `PORT`).
- `src/config.py`: Carga y validación tipada de variables de entorno con valores por defecto y chequeos de presencia.
- `src/services/gemini_service.py`: Cliente y lógica para invocar el modelo de Gemini para texto.
- `src/services/whatsapp_service.py`: Cliente HTTP (`httpx`) para enviar mensajes de vuelta a la API de WhatsApp Cloud (`POST /{PHONE_NUMBER_ID}/messages`).
- `src/main.py`: Aplicación FastAPI con rutas:
  - `GET /health`: Healthcheck para Render / UptimeRobot.
  - `GET /webhook`: Verificación del token y devolución del challenge.
  - `POST /webhook`: Ingesta del payload, extracción del mensaje de texto y despacho asíncrono o inmediato.
- `tests/test_webhook.py`: Pruebas de verificación de token, payload de texto y estados de mensaje.
- `tests/test_gemini.py`: Pruebas unitarias de invocación con mocks del servicio de IA.

## Decisiones de diseño
1. **Framework FastAPI vs Flask:** Se selecciona FastAPI debido a su soporte nativo asíncrono (`async/await`) con `httpx`, ideal para no bloquear el servidor mientras se espera la respuesta de Meta o Gemini.
2. **Desacoplamiento de clientes de servicios:** Se aíslan `gemini_service` y `whatsapp_service` en módulos separados para facilitar pruebas unitarias con mocks sin requerir llamadas reales a la red durante los tests.
3. **Respuesta inmediata HTTP 200 en Webhook:** Meta requiere respuesta rápida (< 3s); el webhook valida el evento y procesa el envío garantizando el código 200 OK para evitar reenvíos de mensajes.

## Cobertura por Requisitos Funcionales
- RF-1 y RF-2: `src/main.py` (endpoint `GET /webhook` verificando `hub.verify_token`).
- RF-3 y RF-6: `src/main.py` (endpoint `POST /webhook` filtrando tipos de mensaje y estados).
- RF-4: `src/services/gemini_service.py` (función generadora de texto).
- RF-5: `src/services/whatsapp_service.py` (función enviadora de mensajes).
- RF-7: `src/main.py` (endpoint `GET /health`).

## Estrategia de pruebas
- Tests unitarios e integración con `pytest` y `pytest-asyncio`.
- Simulación de peticiones HTTP con `httpx.AsyncClient` / `TestClient` de FastAPI.
