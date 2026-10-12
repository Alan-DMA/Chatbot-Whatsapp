# Spec 007 — Personalidad Expresiva y Reacciones Nativas en WhatsApp
Estado: implementada

## Contexto y objetivo
Actualmente, el chatbot responde con un tono neutro y puramente textual o de medios sin aprovechar las capacidades interactivas y emocionales de WhatsApp. Los usuarios (como amigos o familiares) valoran una comunicación más cercana, humana y expresiva. Además, WhatsApp Cloud API permite reaccionar a mensajes individuales con emojis (Reactions), lo que proporciona confirmación visual inmediata y dinamismo a la conversación.

El objetivo de esta especificación es dotar al asistente de una personalidad cálida y empática con uso natural de emojis en sus respuestas, así como la capacidad de reaccionar nativamente con emojis a los mensajes entrantes (fotos, notas de voz, agradecimientos y saludos).

## Usuarios
- Usuarios de WhatsApp que esperan una conversación amigable, humana y enriquecida con emojis y reacciones visuales.
- Administradores que buscan una experiencia de usuario interactiva sin aumentar la latencia ni costos de infraestructura.

## Historias de usuario
- HU-1. Como usuario de WhatsApp, quiero que el asistente responda con un tono cercano, amable y con emojis contextuales para sentir una interacción más natural y agradable.
- HU-2. Como usuario de WhatsApp, quiero que el asistente reaccione con emojis (ej. 👍, ❤️, 👂, 🎨, ✨) a mis mensajes, notas de voz o imágenes para recibir una confirmación inmediata y empática.
- HU-3. Como administrador, quiero que los envíos de reacciones no bloqueen ni retrasen la entrega de la respuesta principal.

## Definiciones
- **Reacción nativa de WhatsApp (Reaction)**: Mensaje interactivo de tipo `reaction` asociado al `message_id` del usuario que superpone un único emoji sobre el globo del mensaje recibido.
- **Personalidad expresiva**: Directiva de estilo conversacional que instruye al modelo a responder de manera empática, clara y acompañada de emojis acordes al tema.

## Requisitos funcionales
- RF-1: CUANDO el usuario envíe cualquier mensaje, EL SISTEMA debe registrar el identificador del mensaje entrante (`message_id`).
- RF-2: CUANDO se reciba un archivo multimedia entrante (nota de voz o imagen), EL SISTEMA debe enviar una reacción de acuse visual (ej. 👂 para audios, 🖼️ o 👀 para imágenes).
- RF-3: CUANDO el usuario envíe un mensaje que exprese agradecimiento o afecto (ej. "gracias", "te quiero", "genial") o reinicio (`/reset`), EL SISTEMA debe enviar una reacción acorde (ej. ❤️, 😊, 👍 o 🔄).
- RF-4: CUANDO la IA genere respuestas conversacionales, EL SISTEMA debe utilizar una personalidad cálida, clara y acompañada de emojis contextuales adecuados.
- RF-5: SI el envío de una reacción falla o es rechazado por la API de mensajería, ENTONCES EL SISTEMA debe continuar con el flujo normal de respuesta sin interrumpir la atención.

## Requisitos no funcionales
- RNF-1: **No bloqueo ni latencia agregada**: Las reacciones deben despacharse de forma asíncrona y resiliente.
- RNF-2: **Compatibilidad nativa**: Las reacciones deben cumplir estrictamente con el estándar de Meta (un solo emoji unicode válido por reacción).

## Casos límite
- Mensajes sin `message_id`: Se omite el envío de reacción y se procede con la respuesta normal.
- El usuario envía un comando de control (ej. `/reset`): Se reacciona con un emoji de confirmación (ej. 🔄 o 👍) y se envía el texto de reinicio.

## Criterios de finalización
- Pruebas automatizadas unitarias y de integración que verifiquen:
  1. Construcción y despacho correcto del payload de reacción a WhatsApp Cloud API.
  2. Invocación de reacciones según el tipo de mensaje entrante.
  3. Resiliencia ante fallos en la llamada a la API de reacciones.
- Suite completa pasando al 100% con `pytest`.
