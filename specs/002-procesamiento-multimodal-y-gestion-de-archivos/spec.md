# Spec 002 — Procesamiento Multimodal y Gestión de Archivos
Estado: implementada

## Contexto y objetivo
El chatbot actualmente procesa y responde únicamente mensajes de texto. Los usuarios de WhatsApp frecuentemente se comunican mediante notas de voz (audio) y capturas o fotografías (imágenes). El objetivo de esta especificación es dotar al sistema de capacidad multimodal para descargar, decodificar, interpretar mediante IA y responder a imágenes y audios, garantizando al mismo tiempo una política estricta de eliminación de archivos temporales para evitar el colapso del almacenamiento efímero en disco.

## Usuarios
- Usuarios de WhatsApp que envían notas de voz o audios y esperan una respuesta inteligente en texto.
- Usuarios de WhatsApp que envían imágenes (con o sin texto/pie de foto explicativo) y esperan análisis o resolución de dudas visuales.

## Historias de usuario
- HU-1. Como usuario de WhatsApp, quiero enviar una nota de voz para recibir una respuesta en formato de nota de voz (audio), manteniendo una conversación hablada y natural.
- HU-2. Como usuario de WhatsApp, quiero enviar una imagen (con o sin texto adicional) para que el asistente analice su contenido visual y me responda en texto.
- HU-3. Como administrador del sistema, quiero que todo archivo descargado o generado (tanto de entrada como de salida) se elimine inmediatamente tras su procesamiento para no saturar el almacenamiento limitado de la máquina o contenedor.

## Definiciones
- **Media ID**: Identificador único proporcionado por WhatsApp en el webhook para un recurso multimedia recibido (imagen o audio).
- **URL temporal de descarga**: Enlace efímero obtenido de la API de mensajería para descargar el binario del medio con cabecera de autorización.
- **Audio OGG Opus**: Formato nativo en el que WhatsApp entrega y reproduce las notas de voz.
- **Transcodificación**: Conversión del archivo de audio comprimido en formato Opus a un formato estándar procesable por el modelo de IA (.mp3 o .wav), y viceversa para el envío de notas de voz de salida a WhatsApp.
- **Text-to-Speech (TTS)**: Conversión del texto generado por Gemini a un archivo de audio para responder al usuario con nota de voz.
- **Limpieza estricta**: Eliminación en bloque de archivos de entrada, transcodificados y de salida generados mediante bloque `finally` o equivalente, garantizando borrado tanto en éxito como en fallo.

## Requisitos funcionales
- RF-1: CUANDO el webhook reciba un mensaje de tipo `image` o `audio`, EL SISTEMA debe extraer el Media ID correspondiente y la información contextual asociada (pie de foto si existe imagen).
- RF-2: CUANDO se extrae un Media ID válido, EL SISTEMA debe solicitar la URL de descarga a la API de WhatsApp y descargar el binario a un archivo temporal local.
- RF-3: CUANDO el medio recibido sea un audio (`audio/ogg; codecs=opus`), EL SISTEMA debe transcodificar el archivo a un formato compatible (.mp3 o .wav) antes de enviarlo a la IA.
- RF-4: CUANDO el medio recibido sea una imagen, EL SISTEMA debe preparar el archivo junto con la instrucción de texto (o una instrucción por defecto si no hay pie de foto) para el modelo de IA.
- RF-5: CUANDO la IA genera la respuesta:
  - SI el mensaje original era una nota de voz, EL SISTEMA debe convertir el texto de respuesta a audio (TTS), transcodificarlo al formato nativo de WhatsApp (OGG Opus) y enviarlo como nota de voz de retorno al usuario.
  - SI el mensaje original era una imagen o texto, EL SISTEMA debe responder con mensaje de texto.
- RF-6: EL SISTEMA debe eliminar todos los archivos temporales (originales de entrada, archivos transcodificados y audios de salida generados) inmediatamente después del intento de procesamiento y envío, tanto si el ciclo fue exitoso como si ocurrió un error.
- RF-7: SI la descarga, la conversión de audio, la inferencia de la IA o la generación de voz fallan, ENTONCES EL SISTEMA debe notificar un mensaje de error amigable al usuario en WhatsApp y garantizar que no queden archivos huérfanos en disco.

## Requisitos no funcionales
- RNF-1: **Higiene de almacenamiento**: Cero fugas de archivos temporales en disco. El espacio ocupado por archivos temporales debe volver a 0 bytes tras cada ciclo de procesamiento.
- RNF-2: **Resiliencia ante fallos**: Un fallo en un archivo individual no debe reiniciar el proceso del servidor ni impedir el procesamiento de solicitudes concurrentes.
- RNF-3: **Compatibilidad de formato**: La transcodificación de audio bidireccional (entrada y salida) debe realizarse mediante `ffmpeg` en el sistema local y herramientas gratuitas/sin costes adicionales.

## Casos límite
- Usuario envía una imagen sin pie de foto (caption vacío o nulo): El sistema debe asumir una solicitud de descripción o análisis general por defecto y responder en texto.
- El archivo de audio entrante está dañado o no puede ser decodificado: El sistema debe capturar el error, limpiar el disco y responder con un mensaje aclaratorio al usuario.
- Fallo en la síntesis o subida del audio de salida: Si el TTS o la subida del audio a WhatsApp falla, el sistema debe degradar elegantemente y enviar la respuesta en texto plano como fallback antes de limpiar el disco.
- El usuario envía formatos no soportados (ej. stickers, videos o documentos no configurados): El sistema debe responder 200 OK al webhook y opcionalmente notificar al usuario sobre los formatos soportados sin colapsar.
- Tiempos de descarga o de procesamiento de audio lentos: El webhook debe responder 200 OK a Meta inmediatamente antes de iniciar la descarga y procesamiento en segundo plano.

## Fuera de alcance
- Soporte para videos y documentos PDF (se reservan para futuras especificaciones).
- Streaming en tiempo real de llamadas de voz de WhatsApp.

## Criterios de finalización
- Pruebas unitarias y de integración pasando al 100% simulando recepción de imagen y audio.
- Comprobación verificable de que ningún archivo queda en disco tras ejecutar los tests o procesar un mensaje.
- Implementación de la suite de tests con mocks para la descarga de medios de Meta y para la API de Gemini.

## Dudas abiertas
- Ninguna. Los requisitos y el objetivo están alineados con la constitución del proyecto y el stack definido.
