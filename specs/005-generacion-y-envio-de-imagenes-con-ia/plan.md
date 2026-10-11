# Plan Técnico — Spec 005: Generación y Envío de Imágenes con IA

## 1. Archivos y responsabilidades
- `src/services/whatsapp_service.py`:
  - Agregar `send_whatsapp_image_message(to_phone_number: str, media_id: str, caption: Optional[str] = None) -> Dict[str, Any]` para despachar mensajes multimedia de tipo `image` a la Meta Cloud API. (Cubre RF-3, RF-4).
- `src/services/gemini_service.py`:
  - Agregar `generate_gemini_image(prompt: str, model: str = "imagen-3.0-generate-002") -> bytes` utilizando `client.aio.models.generate_images(...)` de Google GenAI SDK. (Cubre RF-2, RF-6).
  - Agregar `process_user_message_intent(text: str) -> Dict[str, Any]` con prompt estructurado para discernir si el usuario solicita generar una imagen o continuar la conversación en texto, extrayendo el prompt visual optimizado y el pie de foto. (Cubre RF-1).
- `src/main.py`:
  - Integrar el flujo de detección y generación de imágenes en el webhook `POST /webhook` para mensajes de texto y notas de voz.
  - Asegurar la limpieza atómica de archivos temporales mediante `try...finally: cleanup_files(...)`. (Cubre RF-3, RF-5, RF-7).
- `tests/test_image_generation.py`:
  - Pruebas unitarias e integración de `send_whatsapp_image_message`, `generate_gemini_image`, `process_user_message_intent`, manejo de excepciones y eliminación de temporales en disco. (Cubre RNF-1, RNF-2, RNF-3 y Criterios de finalización).

## 2. Interfaz y tipos
```python
# src/services/whatsapp_service.py
async def send_whatsapp_image_message(
    to_phone_number: str,
    media_id: str,
    caption: Optional[str] = None
) -> Dict[str, Any]: ...

# src/services/gemini_service.py
async def generate_gemini_image(
    prompt: str,
    model: str = "imagen-3.0-generate-002"
) -> bytes: ...

async def process_user_message_intent(
    text: str
) -> Dict[str, Any]:
    # Retorna:
    # {"generate_image": True, "image_prompt": "...", "caption": "..."}
    # o {"generate_image": False, "reply": "..."}
```

## 3. Algoritmo en pseudocódigo
```text
CUANDO llega mensaje de texto:
  intención = await process_user_message_intent(texto)
  SI intención["generate_image"] == True:
    temp_path = crear_archivo_temporal(".jpg")
    try:
      bytes_imagen = await generate_gemini_image(intención["image_prompt"])
      escribir bytes_imagen en temp_path
      media_id = await upload_media_file(temp_path, mime_type="image/jpeg")
      await send_whatsapp_image_message(destinatario, media_id, caption=intención["caption"])
    catch Error:
      await send_whatsapp_text_message(destinatario, "Disculpa, no pude generar la imagen...")
    finally:
      cleanup_files(temp_path)  # Higiene estricta de disco
  SINO:
    await send_whatsapp_text_message(destinatario, intención["reply"])
```

## 4. Decisiones justificadas
1. **Detección unificada de intención y respuesta conversacional en un solo paso:**
   - *Alternativa descartada:* Hacer una llamada de clasificación primero y otra de respuesta después.
   - *Razón:* Duplica la latencia y el consumo de cuota de API. Con un System Prompt estructurado en Gemini 2.5 Flash, el modelo responde en <1s tanto si es conversación como si es solicitud de imagen con prompt enriquecido.
2. **Uso de Imagen 3 (`imagen-3.0-generate-002`) vía `client.aio.models.generate_images`:**
   - *Alternativa descartada:* Llamadas HTTP REST directas o librerías externas de terceros.
   - *Razón:* Soporte oficial en `google-genai` SDK, ejecución asíncrona no bloqueante nativa (`client.aio`) y compatibilidad total con la clave de API ya configurada.
3. **Flujo de subida a Meta mediante `upload_media_file` (`image/jpeg`):**
   - *Alternativa descartada:* Enviar URLs externas públicas a WhatsApp.
   - *Razón:* Meta Cloud API requiere URLs públicas alojadas o subida directa como binario con Media ID. Como Render tiene almacenamiento efímero y no expone bucket S3 público, subir el binario efímero a Meta y luego borrarlo localmente garantiza privacidad, seguridad y cero costes de hosting.

## 5. Estrategia de tests
- Mocks con `unittest.mock.AsyncMock` para `client.aio.models.generate_images` y `upload_media_file`.
- Verificación de borrado de archivos temporales comprobando que `os.path.exists` sea falso tras la ejecución.
- Verificación del payload JSON enviado a WhatsApp (`type="image"`, `caption` presente).
- Ejecución con `pytest`.
