# Tareas — Spec 005: Generación y Envío de Imágenes con IA

- [x] **T1. Función `send_whatsapp_image_message` en `whatsapp_service.py` con tests.** RF-3, RF-4
  - Hecho cuando: La función despacha peticiones `POST` a `/messages` con estructura `type="image"`, `image={"id": media_id, "caption": caption}` y pasa sus pruebas unitarias en `pytest`.

- [x] **T2. Funciones `generate_gemini_image` y `process_user_message_intent` en `gemini_service.py` con tests.** RF-1, RF-2, RF-6
  - Hecho cuando: `generate_gemini_image` sintetiza bytes de imagen vía Imagen 3 y `process_user_message_intent` detecta intenciones de generación y extrae prompts y captions en JSON estructurado, pasando sus pruebas unitarias.

- [x] **T3. Integración de generación de imágenes y limpieza atómica de disco en `src/main.py`.** RF-3, RF-5, RF-7, RNF-1
  - Hecho cuando: El webhook `POST /webhook` despacha la creación de imágenes para texto y audio, sube el archivo a Meta, envía la imagen y elimina de forma garantizada los archivos temporales en bloque `finally`.

- [x] **T4. Verificación integral de la suite de tests (`pytest`) y despliegue a producción.** Criterios de finalización
  - Hecho cuando: Todos los tests pasan al 100% en verde, se verifica la ausencia de archivos residuales en disco y se actualiza `MEMORY.md`.
