# MEMORY.md — Chatbot Multimodal para WhatsApp
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual
- Specs 001 a 007 completadas al 100%.
- Personalidad empática con emojis contextuales y reacciones nativas de WhatsApp implementadas.
- 49 pruebas automatizadas pasando (100% verde).
- Servicio activo en Render (`https://chatbot-whatsapp-614d.onrender.com`).

## Decisiones (y por qué)
- Desacoplamiento modular: `src/config.py`, `src/services/gemini_service.py`, `src/services/whatsapp_service.py`, `src/services/media_service.py`, `src/services/audio_service.py`, `src/services/history_service.py` y `src/main.py`.
- Reacciones nativas en WhatsApp (`send_whatsapp_reaction`): Feedback inmediato y visual (👂 a notas de voz, 👀 a imágenes, ❤️ a afecto/gracias, 🔄 a `/reset`).
- Reacciones no bloqueantes: Se envían con bloques `try/except` silenciosos para garantizar que ningún fallo de reacción impida la entrega de la respuesta principal.
- Personalidad cálida y expresiva: System prompt enriquecido para responder con tono cercano, natural y emojis contextuales.
- Memoria SQLite local (`data/history.db`): Ventana deslizante de 10 turnos con TTL de 45 min y comando `/reset`.

## Aprendizajes y errores a evitar
- El número de prueba de Meta (`+1 555-656-1873`) no permite editar foto de perfil ni nombre comercial (requiere número real propio).
- `GET /webhook` debe responder con `hub.challenge` plano (string), nunca serializado como JSON.
- Asegurar que `POST /webhook` retorne inmediatamente 200 OK aun si el payload no contiene mensajes nuevos.
- Render Free Tier entra en sleep a los 15 min; monitoreo cada 14 min hacia `/ping` o `/health` garantiza actividad continua.

## Próximos pasos
- Disfrutar del bot en WhatsApp con reacciones en vivo, notas de voz, imágenes y memoria activa.
