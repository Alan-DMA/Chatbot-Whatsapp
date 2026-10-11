# Spec 001 — Configuración Core y Conexión de Texto

Estado: implementada

## Contexto y objetivo
Establecer la comunicación bidireccional básica entre WhatsApp Cloud API y el motor de inteligencia artificial de Google (Gemini) para mensajes de texto. Esto permite validar el canal de comunicación, verificar el webhook con los servidores de Meta y procesar mensajes de texto con respuestas generadas por IA.

## Usuarios / actores
- Usuario final de WhatsApp: envía consultas de texto y recibe respuestas en el chat.
- Meta Webhook Service: envía eventos HTTP POST con los mensajes entrantes y verifica el webhook vía HTTP GET.
- Administrador del sistema: configura credenciales, variables de entorno y expone el servidor local con túneles (ngrok).

## Historias de usuario
- HU-1: Como usuario de WhatsApp, quiero enviar un mensaje de texto al bot para recibir una respuesta relevante generada por IA.
- HU-2: Como servidor de Meta, quiero verificar el webhook mediante un challenge GET para confirmar que el servidor está listo para recibir eventos.
- HU-3: Como monitor de disponibilidad, quiero consultar un endpoint de healthcheck para comprobar que el servicio está activo.

## Requisitos funcionales (criterios de aceptación en EARS)
- RF-1: CUANDO Meta envíe una petición `GET /webhook` con `hub.mode=subscribe` y un `hub.verify_token` válido, EL SISTEMA responderá con código HTTP 200 y el valor plano de `hub.challenge`.
- RF-2: SI Meta envía una petición `GET /webhook` con un token de verificación no coincidente, ENTONCES EL SISTEMA responderá con código HTTP 403 Forbidden.
- RF-3: CUANDO Meta envíe una petición `POST /webhook` con un payload JSON de mensaje de texto válido, EL SISTEMA responderá inmediatamente con código HTTP 200 OK y procesará el mensaje.
- RF-4: CUANDO se reciba el texto del usuario, EL SISTEMA enviará el mensaje al modelo de Google Gemini y obtendrá la respuesta textual generada.
- RF-5: CUANDO Gemini devuelva la respuesta, EL SISTEMA enviará una petición POST a la API de WhatsApp Cloud (`/messages`) con el texto de respuesta hacia el número del usuario remitente.
- RF-6: SI el payload del webhook corresponde a un estado (status: sent, delivered, read) o a un formato no soportado en esta fase, ENTONCES EL SISTEMA ignorará el procesamiento de IA y retornará código HTTP 200 OK.
- RF-7: CUANDO se consulte la ruta `GET /health`, EL SISTEMA responderá con código HTTP 200 OK y estado operativo.

## Requisitos no funcionales
- Rendimiento: La respuesta inicial al webhook de Meta debe ocurrir en menos de 3 segundos para evitar reintentos duplicados por timeout de Meta.
- Seguridad: No registrar tokens de Meta ni claves de API de Gemini en logs. Todas las credenciales se cargan desde variables de entorno.
- Compatibilidad: Estructura compatible con Python 3.11+ y despliegue en contenedor Docker.

## Casos límite
- Mensaje con cuerpo vacío o solo espacios.
- Notificaciones duplicadas de Meta (mismo `wamid`).
- Caída o fallo temporal de la API de Gemini (retornar mensaje de cortesía al usuario sin provocar caída del webhook).
- Mensajes enviados por el propio bot (ignorar para evitar bucles infinitos).

## Fuera de alcance
- Descarga y transcodificación de notas de voz con ffmpeg (se abordará en la spec 002).
- Procesamiento y análisis visual de imágenes (se abordará en la spec 003).
- Persistencia de historial de conversaciones en base de datos externa.

## Criterios de finalización
- Verificación del webhook completada exitosamente ante Meta.
- Envío de un mensaje de prueba de WhatsApp y recepción de la respuesta generada por Gemini.
- Suite de pruebas automatizadas (`pytest`) en verde cubriendo verificación GET, recepción POST y mock de respuesta a WhatsApp.

## Dudas abiertas
- [NECESITA ACLARACIÓN] ¿Prefieres FastAPI o Flask como framework web base para el servidor? (Se recomienda FastAPI por async nativo y validación tipada con Pydantic).
