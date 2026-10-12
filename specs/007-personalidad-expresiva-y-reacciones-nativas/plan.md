# Plan Técnico — Spec 007: Personalidad Expresiva y Reacciones Nativas en WhatsApp

## 1. Archivos y responsabilidades
- `src/services/whatsapp_service.py`:
  - Implementar `send_whatsapp_reaction(to_phone_number: str, message_id: str, emoji: str) -> Dict[str, Any]` que construye el payload `type="reaction"` y lo envía a Meta Graph API (`/messages`). (Cubre RF-1, RF-2, RF-3, RNF-2).
- `src/services/gemini_service.py`:
  - Actualizar el System Instruction en `process_user_message_intent`, `generate_gemini_text_response` y `generate_gemini_multimodal_response` para definir la personalidad cálida, cercana, atenta y con uso natural de emojis. (Cubre RF-4).
- `src/main.py`:
  - Extraer `message_id` en el webhook.
  - Despachar reacciones de acuse/contexto (ej. 👂 para audio, 👀 para imagen, ❤️ para afecto/agradecimiento, 🔄 para `/reset`) de forma resiliente (`try/except`) sin bloquear el flujo principal. (Cubre RF-1, RF-2, RF-3, RF-5, RNF-1).
- `tests/test_whatsapp.py`:
  - Pruebas unitarias de `send_whatsapp_reaction`.
- `tests/test_webhook_receiver.py`:
  - Pruebas de integración verificando el despacho de reacciones según el mensaje entrante.

## 2. Interfaz
```python
async def send_whatsapp_reaction(
    to_phone_number: str,
    message_id: str,
    emoji: str
) -> Dict[str, Any]:
    """
    Envía una reacción (emoji) sobre un mensaje específico en WhatsApp.
    Endpoint: POST https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages
    """
    ...
```

## 3. Decisiones justificadas
1. **Reacciones no bloqueantes con captura de excepción:**
   - *Razón:* Si Meta rechaza una reacción (por ejemplo, porque el mensaje era muy viejo o el emoji no es compatible), el bot nunca debe fallar en entregar el mensaje de texto o audio de respuesta.
2. **Determinación ligera de reacciones en webhook:**
   - *Razón:* Para audios e imágenes, el emoji es inmediato (👂 y 👀), dando feedback instantáneo mientras Gemini procesa el contenido. Para texto, saludos, agradecimientos o `/reset` se detectan rápidamente por palabras clave o contexto.
