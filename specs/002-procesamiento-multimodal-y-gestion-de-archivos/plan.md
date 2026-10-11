# Plan Técnico — Spec 002: Procesamiento Multimodal y Gestión de Archivos

## Archivos y responsabilidades
- `src/services/media_service.py`:
  - Obtención de URL temporal de descarga desde Meta Graph API (`GET /{media_id}`).
  - Descarga autenticada del binario a almacenamiento temporal (`tempfile`).
  - Subida de archivos binarios (para nota de voz de salida) a Meta Graph API (`POST /{phone_number_id}/media`).
  - Utilidad de limpieza atómica de archivos (`cleanup_files(*paths)`).
- `src/services/audio_service.py`:
  - Conversión local con `ffmpeg` de audio OGG Opus entrante a formato compatible (.mp3 / .wav).
  - Síntesis de voz (TTS) y conversión del audio resultante a OGG Opus nativo de WhatsApp.
- `src/services/gemini_service.py`:
  - Extensión para soportar llamadas multimodales enviando imagen + prompt o audio + prompt a Gemini.
- `src/services/whatsapp_service.py`:
  - Añadir soporte para envío de mensajes de tipo `audio` (notas de voz con `type="audio"` y `audio={"id": media_id}`).
- `src/main.py`:
  - Detección de tipo de mensaje en `POST /webhook` (`text`, `image`, `audio`).
  - Orquestación en background task del flujo multimodal con garantía de limpieza en bloque `finally`.

## Decisiones justificadas
1. **TTS ligero sin dependencias de pago**: Usar una solución gratuita de síntesis de voz (como `gTTS` o `edge-tts`) procesada localmente y convertida con `ffmpeg` a Opus nativo de WhatsApp.
2. **Ciclo de vida en bloque `finally`**: Todos los paths temporales creados se registran en una lista y se eliminan incondicionalmente en `finally: cleanup_files(...)` para asegurar RF-6 y RNF-1.
3. **Mocks para pruebas**: `pytest` simulará las llamadas a Meta Graph API (descarga/subida) y a Gemini sin depender de internet ni de llamadas reales a producción.
