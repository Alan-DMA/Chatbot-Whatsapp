# MEMORY.md — Chatbot Multimodal para WhatsApp
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual
- Specs 001, 002, 003, 004 y 005 completadas al 100%.
- Bot multimodal con generación visual activo en Render (`https://chatbot-whatsapp-614d.onrender.com`).
- 37 pruebas automatizadas pasando (100% verde).

## Decisiones (y por qué)
- Desacoplamiento modular: `src/config.py`, `src/services/gemini_service.py`, `src/services/whatsapp_service.py`, `src/services/media_service.py`, `src/services/audio_service.py` y `src/main.py`.
- Generación de imágenes: `generate_gemini_image` con Imagen 3 (`imagen-3.0-generate-002`) vía `client.aio.models.generate_images`.
- Detección de intención unificada: `process_user_message_intent` resuelve si es chat estándar o generación visual en una única llamada, extrayendo prompt optimizado en inglés y caption cordial en español.
- Despacho multimedia en WhatsApp: `send_whatsapp_image_message` envía imágenes vía Meta Cloud API usando Media ID y caption.
- Limpieza atómica: `cleanup_files` elimina imágenes generadas temporales en bloque `finally` para estricta higiene de almacenamiento efímero.
- Resiliencia ante timeouts: Captura de `httpx.TimeoutException` en llamadas a Meta y Gemini sin afectar el ciclo del webhook.

## Aprendizajes y errores a evitar
- Modelos estándar como `gemini-2.5-flash` alucinan si se les pide generar imágenes directamente en chat sin tool o pipeline a Imagen 3.
- `GET /webhook` debe responder con `hub.challenge` plano (string), nunca serializado como JSON.
- Asegurar que `POST /webhook` retorne inmediatamente 200 OK aun si el payload no contiene mensajes nuevos.
- Render Free Tier entra en sleep a los 15 min; monitoreo cada 14 min hacia `/ping` o `/health` garantiza actividad continua.

## Próximos pasos
- Desplegar cambios en Render vía push a GitHub y disfrutar de la generación de imágenes en WhatsApp.
