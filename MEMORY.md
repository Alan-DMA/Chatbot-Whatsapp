# MEMORY.md — Chatbot Multimodal para WhatsApp
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual
- Spec 001 y Spec 002 completadas al 100%.
- Spec 003 en curso: T1 y T2 completadas (`Dockerfile`, `.dockerignore`, `.gitignore`, repo Git inicializado y commiteado con 0 fugas de secretos).
- 26 pruebas automatizadas pasando (100% verde).

## Decisiones (y por qué)
- Desacoplamiento modular: `src/config.py`, `src/services/gemini_service.py`, `src/services/whatsapp_service.py`, `src/services/media_service.py`, `src/services/audio_service.py` y `src/main.py`.
- Flujo asíncrono no bloqueante: Garantiza respuesta HTTP 200 a Meta en < 3s evitando duplicados y timeouts.
- Inferencia multimodal nativa: `generate_gemini_multimodal_response` usa `genai.types.Part.from_bytes` para imágenes y audios.
- Síntesis y notas de voz nativas: `convert_text_to_whatsapp_voice_note` genera audio con `gTTS` y lo transcodifica a Opus con `ffmpeg` (`libopus`, 32k VBR) para que WhatsApp lo reconozca como nota de voz reproducible.
- Subida de medios a Meta: `upload_media_file` sube el audio generado mediante `POST /{phone_number_id}/media` y `send_whatsapp_audio_message` lo envía.
- Limpieza atómica: `cleanup_files` elimina archivos de entrada, salida y temporales intermedios en bloque `finally`.
- Contenedor con puerto dinámico: `Dockerfile` ejecuta `uvicorn` resolviendo `${PORT:-8000}` para compatibilidad total con Render Free Tier.

## Aprendizajes y errores a evitar
- `GET /webhook` debe responder con `hub.challenge` plano (string), nunca serializado como JSON.
- Asegurar que `POST /webhook` retorne inmediatamente 200 OK aun si el payload no contiene mensajes nuevos.
- **Suscripción de WABA obligatoria:** En WhatsApp Cloud API no basta con registrar el Webhook en la App; se debe invocar `POST /{WABA_ID}/subscribed_apps` con el token para que Meta despache los mensajes entrantes al webhook.
- Para túneles locales en desarrollo, Cloudflare Tunnel (`cloudflared`) evita bloqueos de páginas intermedias que ocurren con localtunnel.

## Próximos pasos
- Spec 003 T3: Subir código a repositorio de GitHub y conectar a Render Web Service.
- Spec 003 T4: Configurar variables de entorno en Render y apuntar Webhook de Meta al dominio de Render.
