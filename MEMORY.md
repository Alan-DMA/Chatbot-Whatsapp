# MEMORY.md — Chatbot Multimodal para WhatsApp
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual
- Specs 001, 002 y 003 completadas al 100%.
- Despliegue en la nube completado en Render (`https://chatbot-whatsapp-614d.onrender.com`).
- Contenedor Docker con Python 3.11 y `ffmpeg` operando 24/7.
- Monitoreo `/health` respondiendo 200 OK.
- 26 pruebas automatizadas pasando (100% verde).

## Decisiones (y por qué)
- Desacoplamiento modular: `src/config.py`, `src/services/gemini_service.py`, `src/services/whatsapp_service.py`, `src/services/media_service.py`, `src/services/audio_service.py` y `src/main.py`.
- Flujo asíncrono no bloqueante: Garantiza respuesta HTTP 200 a Meta en < 3s evitando duplicados y timeouts.
- Inferencia multimodal nativa: `generate_gemini_multimodal_response` usa `genai.types.Part.from_bytes` para imágenes y audios.
- Síntesis y notas de voz nativas: `convert_text_to_whatsapp_voice_note` genera audio con `gTTS` y lo transcodifica a Opus con `ffmpeg` (`libopus`, 32k VBR).
- Limpieza atómica: `cleanup_files` elimina archivos de entrada, salida y temporales intermedios en bloque `finally`.
- Contenedor con puerto dinámico: `Dockerfile` ejecuta `uvicorn` resolviendo `${PORT:-8000}` para compatibilidad nativa con Render.

## Aprendizajes y errores a evitar
- `GET /webhook` debe responder con `hub.challenge` plano (string), nunca serializado como JSON.
- Asegurar que `POST /webhook` retorne inmediatamente 200 OK aun si el payload no contiene mensajes nuevos.
- **Suscripción de WABA obligatoria:** En WhatsApp Cloud API no basta con registrar el Webhook en la App; se debe invocar `POST /{WABA_ID}/subscribed_apps` con el token para que Meta despache los mensajes entrantes al webhook.
- Para evitar que la instancia Free Tier de Render entre en reposo (sleep) tras 15 min de inactividad, configurar UptimeRobot con pings cada 14 min hacia `/health`.

## Próximos pasos
- Spec 004 redactada en borrador (`specs/004-alta-disponibilidad-y-optimizacion-continua/spec.md`). Pendiente visto bueno para redactar plan técnico y tareas.
- Monitoreo UptimeRobot cada 14 min a `/ping` en producción.
