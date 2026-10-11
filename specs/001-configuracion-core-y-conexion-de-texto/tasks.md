# Tareas 001 — Configuración Core y Conexión de Texto

- [x] **T1: Configuración de dependencias y variables de entorno.**
  - RF cubiertos: Base arquitectónica.
  - Hecho cuando: Existan `requirements.txt`, `.env.example`, y `src/config.py` cargue correctamente la configuración.

- [x] **T2: Endpoint de Healthcheck y verificación de Webhook de Meta (GET).**
  - RF cubiertos: RF-1, RF-2, RF-7.
  - Hecho cuando: `pytest` valide que `GET /health` retorne 200 OK y `GET /webhook` retorne 200 con el challenge si el token coincide, o 403 si no coincide.

- [x] **T3: Servicio de envío de mensajes hacia WhatsApp Cloud API.**
  - RF cubiertos: RF-5.
  - Hecho cuando: `tests/test_whatsapp.py` valide la construcción correcta del payload JSON hacia `https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages` mediante mock HTTP.

- [x] **T4: Servicio de procesamiento de texto con Google Gemini.**
  - RF cubiertos: RF-4.
  - Hecho cuando: `src/services/gemini_service.py` invoque el modelo de IA con el prompt del usuario y los tests con mock devuelvan la respuesta esperada.

- [x] **T5: Integración del Webhook receptor (POST) y flujo completo de texto.**
  - RF cubiertos: RF-3, RF-4, RF-5, RF-6.
  - Hecho cuando: Un test de integración simule un POST con payload de texto de Meta, active el flujo hacia Gemini y despache el mensaje de respuesta a WhatsApp, retornando 200 OK.
