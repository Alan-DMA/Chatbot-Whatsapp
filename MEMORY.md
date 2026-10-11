# MEMORY.md — Chatbot Multimodal para WhatsApp
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual
- Specs 001 a 006 completadas al 100%.
- Memoria conversacional con SQLite local, ventana deslizante (10 turnos) y TTL (45 min) implementada.
- Bot multimodal con generación visual y memoria activo en Render (`https://chatbot-whatsapp-614d.onrender.com`).
- 46 pruebas automatizadas pasando (100% verde).

## Decisiones (y por qué)
- Desacoplamiento modular: `src/config.py`, `src/services/gemini_service.py`, `src/services/whatsapp_service.py`, `src/services/media_service.py`, `src/services/audio_service.py`, `src/services/history_service.py` y `src/main.py`.
- Memoria SQLite local (`data/history.db`): Cero costo, cero dependencias externas, latencia <1 ms y aislamiento estricto por número de teléfono.
- Ventana deslizante y TTL: Conserva los últimos 10 turnos (20 mensajes) y purga tras 45 min de inactividad para evitar desbordes de memoria y mezcla de temas viejos.
- Soporte para comando `/reset`: Permite al usuario borrar su historial manualmente en cualquier momento.
- Inyección de contexto estructurado: `process_user_message_intent` incluye el historial reciente directamente en el prompt para resolver referencias pasadas (como "¿cuál era la opción 2?").
- Generación de imágenes: `generate_gemini_image` con Imagen 3 (`imagen-3.0-generate-002`) vía `client.aio.models.generate_images`.
- Limpieza atómica: `cleanup_files` elimina imágenes y audios temporales en bloque `finally`.

## Aprendizajes y errores a evitar
- Modelos estándar como `gemini-2.5-flash` alucinan si se les pide generar imágenes directamente en chat sin tool o pipeline a Imagen 3.
- `GET /webhook` debe responder con `hub.challenge` plano (string), nunca serializado como JSON.
- Asegurar que `POST /webhook` retorne inmediatamente 200 OK aun si el payload no contiene mensajes nuevos.
- Render Free Tier entra en sleep a los 15 min; monitoreo cada 14 min hacia `/ping` o `/health` garantiza actividad continua.

## Próximos pasos
- Desplegar cambios en Render vía push a GitHub y disfrutar de conversaciones fluidas con memoria en WhatsApp.
