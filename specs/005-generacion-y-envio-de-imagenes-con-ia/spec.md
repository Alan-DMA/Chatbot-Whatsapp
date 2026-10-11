# Spec 005 — Generación y Envío de Imágenes con IA
Estado: implementada

## Contexto y objetivo
Actualmente, el asistente multimodal es capaz de interpretar texto, notas de voz e imágenes entrantes. Sin embargo, cuando un usuario solicita explícitamente crear, dibujar o generar una imagen (o confirma una propuesta visual previa), el modelo conversacional puede generar respuestas de texto donde promete o describe la imagen sin llegar a entregar ningún archivo visual real, provocando confusión y alucinaciones en el diálogo.

El objetivo de esta especificación es dotar al sistema de la capacidad de identificar solicitudes de generación visual, sintetizar la imagen requerida a través de IA generativa, enviarla directamente al chat de mensajería como un mensaje multimedia adjunto y asegurar la eliminación estricta de cualquier archivo temporal generado.

## Usuarios
- Usuarios de mensajería que solicitan crear, ilustrar o representar conceptos visuales mediante texto o notas de voz.
- Administradores del sistema que requieren mantener la higiene del almacenamiento efímero y la estabilidad operativa del servicio.

## Historias de usuario
- HU-1. Como usuario de mensajería, quiero pedirle al asistente que genere o dibuje una imagen descriptiva (en texto o nota de voz) para recibir una imagen real en mi conversación.
- HU-2. Como usuario de mensajería, quiero que la imagen generada llegue acompañada de un pie de foto explicativo para contextualizar lo que fue creado.
- HU-3. Como administrador del sistema, quiero que todo archivo de imagen generado y almacenado temporalmente se elimine de forma garantizada e inmediata tras su transmisión para proteger el almacenamiento limitado.

## Definiciones
- **Generación de imágenes con IA**: Proceso de síntesis visual automática a partir de una descripción conceptual en lenguaje natural (*text-to-image*).
- **Mensaje multimedia de tipo imagen**: Mensaje de salida entregado a través del servicio de mensajería que contiene un archivo visual renderizable directamente en el chat junto con un pie de foto opcional.
- **Solicitud de imagen**: Mensaje de entrada (recibido por texto o nota de voz) donde el usuario manifiesta la intención de producir una imagen o confirma una propuesta visual previa.
- **Limpieza atómica de archivo generado**: Eliminación garantizada del archivo temporal local mediante mecanismos de manejo de excepciones y bloques de finalización, asegurando borrado tanto en ejecuciones exitosas como con errores.

## Requisitos funcionales
- RF-1: CUANDO el usuario envíe un mensaje (por texto o nota de voz) que solicite la creación, generación o dibujo de una imagen, EL SISTEMA debe identificar la intención de generación de imagen y extraer la descripción visual correspondiente.
- RF-2: CUANDO se identifique una intención válida de generación de imagen, EL SISTEMA debe invocar el servicio de generación visual para sintetizar la imagen solicitada.
- RF-3: CUANDO la imagen se genere exitosamente, EL SISTEMA debe entregar el archivo al usuario a través del servicio de mensajería como un mensaje multimedia de tipo imagen.
- RF-4: CUANDO la imagen sea enviada, EL SISTEMA debe incluir un pie de foto explicativo o de confirmación acompañando a la imagen.
- RF-5: EL SISTEMA debe eliminar todo archivo de imagen generado temporalmente en el almacenamiento local inmediatamente después de su transmisión o intento de envío.
- RF-6: SI el servicio de generación visual rechaza la solicitud o no puede sintetizar la imagen (por restricciones de seguridad, sobrecarga o fallo de servicio), ENTONCES EL SISTEMA debe notificar al usuario con un mensaje explicativo y cordial sin colapsar el servicio.
- RF-7: SI ocurre un error al transmitir o entregar la imagen generada mediante el servicio de mensajería, ENTONCES EL SISTEMA debe notificar al usuario el fallo y garantizar la eliminación inmediata del archivo temporal local.

## Requisitos no funcionales
- RNF-1: **Higiene de almacenamiento**: Cero persistencia de archivos de imagen temporales en disco tras la finalización de cada ciclo de generación y envío.
- RNF-2: **Resiliencia y procesamiento asíncrono**: La generación y transmisión de la imagen debe gestionarse en segundo plano sin retrasar la respuesta inmediata de recepción (HTTP 200) requerida por la plataforma de mensajería.
- RNF-3: **Experiencia de usuario nativa**: La imagen debe entregarse visible directamente dentro de la interfaz del chat del usuario, sin requerir redirecciones a enlaces externos.

## Casos límite
- El usuario solicita una imagen mediante una referencia indirecta o confirmación a un diálogo previo (ej. "genera la segunda opción", "dibuja lo que me dijiste"): El sistema debe ser capaz de contextualizar la descripción necesaria para la síntesis de la imagen.
- El usuario solicita una imagen a través de una nota de voz: El sistema debe transcribir e interpretar la solicitud de audio, generar la imagen y responder con el archivo visual y su pie de foto.
- Solicitudes que incumplan filtros de seguridad o políticas del modelo generador: El sistema debe capturar el rechazo amigablemente y responder en texto explicando la imposibilidad de generar esa imagen específica.
- Fallos transitorios de red o tiempo de espera agotado al subir la imagen: El sistema debe atrapar la excepción, notificar al usuario la dificultad temporal y purgar el archivo del disco local.

## Fuera de alcance
- Edición interactiva avanzada de imágenes por regiones (*in-painting* / retoques guiados por máscaras).
- Generación de videos o animaciones.

## Criterios de finalización
- Pruebas automatizadas unitarias y de integración que verifiquen:
  1. Detección de intención de generación de imágenes.
  2. Síntesis y almacenamiento temporal del archivo visual.
  3. Despacho como mensaje de imagen hacia la API de mensajería con su pie de foto.
  4. Borrado estricto y total del archivo de imagen generado en disco tanto en éxito como en fallo.
- Cobertura de tests ejecutada y pasando al 100%.

## Dudas abiertas
- Ninguna. Los requisitos están alineados con la constitución del proyecto y el comportamiento esperado.
