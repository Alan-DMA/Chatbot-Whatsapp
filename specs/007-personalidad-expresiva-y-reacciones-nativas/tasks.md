# Tareas — Spec 007: Personalidad Expresiva y Reacciones Nativas en WhatsApp

- [x] **T1. Función `send_whatsapp_reaction` en `whatsapp_service.py` con tests unitarios.** RF-1, RNF-2
  - Hecho cuando: Envía el payload `type="reaction"` con `message_id` y `emoji` a Meta, pasando sus tests en `tests/test_whatsapp.py`.

- [x] **T2. Enriquecimiento del System Prompt con personalidad y emojis en `gemini_service.py`.** RF-4
  - Hecho cuando: Las instrucciones del sistema promueven un tono empático, cálido y con emojis contextuales en las respuestas, pasando la suite de `tests/test_gemini.py`.

- [x] **T3. Integración de reacciones automáticas y resilientes en `src/main.py` con tests.** RF-1, RF-2, RF-3, RF-5, RNF-1
  - Hecho cuando: El webhook envía reacciones inmediatas a audios (👂), imágenes (👀), agradecimientos/afecto (❤️/👍) y reinicios (🔄) sin bloquear la respuesta principal, pasando sus tests en `tests/test_webhook_receiver.py`.

- [x] **T4. Verificación integral de tests (`pytest`), actualización de `MEMORY.md` y despliegue a producción.** Criterios de finalización
  - Hecho cuando: Toda la suite pasa al 100% en verde, se actualiza `MEMORY.md` y se sube el commit a GitHub para despliegue en Render.
