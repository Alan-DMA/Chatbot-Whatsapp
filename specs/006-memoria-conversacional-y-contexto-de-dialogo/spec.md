# Spec 006 — Memoria Conversacional y Contexto de Diálogo
Estado: implementada

## Contexto y objetivo
Actualmente, las interacciones con el asistente son completamente aisladas (sin estado previo). Cuando un usuario hace referencia a un mensaje anterior (por ejemplo, eligiendo "la opción 2", pidiendo "continúa", o solicitando cambios sobre una idea previa), el sistema no dispone de la memoria del diálogo y responde como si fuera el primer contacto.

El objetivo de esta especificación es dotar al sistema de persistencia y gestión de contexto conversacional por usuario con ventana temporal de inactividad (TTL) y límite de mensajes (ventana deslizante), permitiendo conversaciones coherentes y contextuales.

## Usuarios
- Usuarios de mensajería que esperan que el asistente recuerde el hilo de la conversación activa y comprenda referencias a propuestas previas.
- Administradores del sistema que requieren mantener un uso acotado de almacenamiento y tokens, garantizando aislamiento estricto entre usuarios.

## Historias de usuario
- HU-1. Como usuario de mensajería, quiero que el asistente recuerde los mensajes recientes de nuestra conversación activa para poder responder con referencias directas (como "la opción 2" o "cambia el estilo") sin repetir toda la información.
- HU-2. Como usuario de mensajería, quiero que tras un periodo prolongado de inactividad la conversación se reinicie de forma limpia para no mezclar temas obsoletos.
- HU-3. Como usuario de mensajería, quiero poder solicitar expresamente el reinicio de la memoria del diálogo para comenzar un tema desde cero en cualquier momento.
- HU-4. Como administrador del sistema, quiero que el historial tenga un límite máximo de mensajes recientes por usuario para evitar el consumo desmedido de memoria y tokens.

## Definiciones
- **Turno conversacional**: Unidad compuesta por el mensaje enviado por el usuario y la respuesta emitida por el asistente.
- **Identificador de sesión**: Identificador único del usuario (número de teléfono) que delimita su espacio de memoria.
- **Ventana deslizante de contexto**: Mecanismo que retiene únicamente los últimos $N$ turnos de diálogo, descartando automáticamente los más antiguos.
- **Tiempo de vida por inactividad (TTL)**: Tiempo máximo transcurrido sin nuevos mensajes tras el cual la sesión anterior se considera expirada y se reinicia.

## Requisitos funcionales
- RF-1: CUANDO el usuario envíe un mensaje, EL SISTEMA debe recuperar el historial conversacional activo asociado a su identificador de sesión.
- RF-2: SI el tiempo transcurrido desde el último mensaje del usuario supera el tiempo de vida por inactividad (TTL), ENTONCES EL SISTEMA debe reiniciar el historial e iniciar una conversación limpia.
- RF-3: CUANDO se procese la consulta con el modelo de inteligencia artificial, EL SISTEMA debe suministrar el historial conversacional acumulado junto con el nuevo mensaje del usuario para preservar el contexto del diálogo.
- RF-4: CUANDO el asistente genere una respuesta (sea texto o confirmación de imagen generada), EL SISTEMA debe registrar tanto el mensaje del usuario como la respuesta generada en el historial de la sesión.
- RF-5: MIENTRAS el historial conversacional supere el tamaño de la ventana deslizante permitida, EL SISTEMA debe descartar los turnos más antiguos, conservando intactos los más recientes.
- RF-6: SI el usuario envía un mensaje de reinicio explícito (como "/reset", "reiniciar conversación" o "borrar memoria"), ENTONCES EL SISTEMA debe purgar el historial activo de dicho usuario y confirmar el reinicio del diálogo.
- RF-7: SI ocurre un fallo en el almacenamiento o lectura del historial, ENTONCES EL SISTEMA debe continuar respondiendo al mensaje actual de forma resiliente sin memoria previa, evitando interrumpir el servicio.

## Requisitos no funcionales
- RNF-1: **Aislamiento absoluto**: Las conversaciones de diferentes usuarios no deben mezclarse bajo ninguna circunstancia.
- RNF-2: **Latencia mínima**: Las operaciones de lectura y guardado de contexto deben ser de acceso local ultrarrápido sin impactar el tiempo de respuesta del chatbot.
- RNF-3: **Consumo eficiente y acotado**: El tamaño de la base de datos o almacenamiento local debe mantenerse contenido mediante la eliminación periódica o depuración de sesiones expiradas.

## Casos límite
- Primer mensaje de un usuario nuevo: Se inicializa la sesión sin historial previo.
- El usuario envía una nota de voz: El texto interpretado y la respuesta emitida deben almacenarse en el historial para mantener la continuidad si el usuario alterna entre voz y texto.
- Mensaje recibido en el límite exacto del TTL: Si se supera el límite de inactividad, se limpia el historial antes de procesar el nuevo mensaje.
- Solicitudes de generación de imágenes contextuales: Si el usuario dice "haz la opción 2" habiendo recibido antes dos propuestas de dibujo, la IA debe usar el contexto previo para inferir la descripción de la opción elegida.

## Fuera de alcance
- Almacenamiento a largo plazo durante meses (búsqueda semántica histórica o bases vectoriales RAG).
- Compartir memoria entre diferentes números de teléfono.

## Criterios de finalización
- Pruebas automatizadas unitarias y de integración que verifiquen:
  1. Guardado y recuperación ordenada de turnos de diálogo por identificador de usuario.
  2. Poda automática por ventana deslizante (máximo de turnos configurado).
  3. Expiración de historial por inactividad tras el TTL establecido.
  4. Comando de reinicio explícito de conversación.
  5. Inclusión correcta del historial en las peticiones a la IA.
  6. Resiliencia ante fallos en la capa de datos.
- Cobertura de tests ejecutada y pasando al 100%.

## Dudas abiertas
- Ninguna.
