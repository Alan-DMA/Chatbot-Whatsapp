# Tareas — Spec 002: Procesamiento Multimodal y Gestión de Archivos

- [x] **T1. Servicio de medios y descarga autenticada desde Meta.** RF-1, RF-2, RF-6
  - Hecho cuando: Exista `src/services/media_service.py` con funciones para consultar la URL de un `media_id`, descargar el archivo temporalmente y una rutina `cleanup_files(*paths)` probada con tests unitarios en verde.
- [x] **T2. Conversión de audio entrante con ffmpeg.** RF-3, RNF-3
  - Hecho cuando: Exista función en `src/services/audio_service.py` que transcodifique `.ogg` Opus a `.mp3`/`.wav` mediante subproceso seguro y pase pruebas con mocks y archivos de prueba.
- [x] **T3. Procesamiento multimodal en Gemini (imágenes y audio).** RF-3, RF-4
  - Hecho cuando: `src/services/gemini_service.py` soporte generar respuestas a partir de archivos de audio e imagen con tests automatizados pasando.
- [x] **T4. Síntesis de voz (TTS) y envío de notas de voz de salida.** RF-5
  - Hecho cuando: Se genere audio de respuesta a partir de texto, se transcodifique a Opus nativo de WhatsApp, se suba a Meta y se envíe mediante `whatsapp_service.py` con tests pasando.
- [x] **T5. Integración en webhook, orquestación y limpieza estricta.** RF-1, RF-5, RF-6, RF-7
  - Hecho cuando: `src/main.py` maneje `image` y `audio`, orqueste la respuesta en background y garantice el borrado de temporales en `finally`, con suite completa de tests de integración en verde.
