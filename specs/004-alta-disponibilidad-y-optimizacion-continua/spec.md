# Spec 004 — Alta Disponibilidad y Optimización Continua
Estado: implementada

## Contexto y objetivo
Render Free Tier suspende las instancias tras 15 minutos continuos sin tráfico entrante (modo sleep), provocando que las peticiones posteriores de WhatsApp sufran demoras de arranque en frío (cold start de 50+ segundos) o fallen por timeout de Meta (< 3s). Asimismo, la integración depende de APIs externas (Meta Graph API y Google Gemini) que pueden experimentar latencia o desconexiones temporales. El objetivo de esta especificación es mantener el servicio activo 24/7 mediante monitoreo automatizado con UptimeRobot y blindar la aplicación con manejo integral de excepciones y timeouts resilientes.

## Usuarios
- Usuarios de WhatsApp que esperan respuestas instantáneas sin demoras por suspensión de instancia.
- Administradores del sistema que requieren visibilidad continua sobre la salud operativa del bot.

## Historias de usuario
- HU-1. Como usuario de WhatsApp, quiero que el bot responda de inmediato en cualquier momento del día o de la noche sin retrasos por hibernación del servidor.
- HU-2. Como administrador del sistema, quiero disponer de una ruta de chequeo ultraligera (`/ping`) para que servicios externos como UptimeRobot mantengan despierto el contenedor cada 14 minutos.
- HU-3. Como administrador del sistema, quiero que cualquier timeout o fallo transitorio de Meta o Google sea contenido limpiamente con un mensaje de fallback amigable al usuario sin tumbar el backend.

## Definiciones
- **Modo Sleep de Render**: Hibernación automática del contenedor gratuito tras 15 minutos de inactividad de red.
- **Cold Start**: Retraso de reactivación del contenedor hibernado (30 a 60 segundos).
- **Ruta `/ping`**: Endpoint HTTP GET mínimo que responde de forma inmediata HTTP 200 OK sin tocar bases de datos ni servicios externos.
- **Timeout Resiliente**: Límite de tiempo máximo para peticiones externas con captura de `httpx.TimeoutException` y excepciones del SDK de Gemini, garantizando que el usuario reciba un aviso oportuno.

## Requisitos funcionales
- RF-1: EL SISTEMA debe exponer una ruta HTTP `GET /ping` que responda inmediatamente con código de estado HTTP 200 OK y carga útil JSON indicando estado activo (`{"status": "alive"}`).
- RF-2: EL SISTEMA debe garantizar que la ruta `/ping` no consuma dependencias externas ni realice operaciones de E/S pesadas para responder en menos de 50 milisegundos.
- RF-3: EL SISTEMA debe envolver todas las llamadas salientes a Meta Graph API y Google GenAI en bloques `try/except` que capturen explícitamente excepciones de tiempo de espera (`httpx.TimeoutException`, errores de conexión o timeouts de inferencia).
- RF-4: CUANDO ocurra un timeout o fallo de red con Meta o Gemini, EL SISTEMA debe registrar el evento con `logger.error` e intentar notificar un mensaje de respaldo al usuario sin interrumpir el bucle de eventos del servidor.
- RF-5: EL SISTEMA debe documentar y verificar la configuración de UptimeRobot ejecutando peticiones periódicas a `/ping` cada 14 minutos para neutralizar el modo sleep.

## Requisitos no funcionales
- RNF-1: **Disponibilidad Continua**: El servicio debe mantenerse activo 24/7 en la capa gratuita de Render.
- RNF-2: **Tiempos de Respuesta de Healthcheck**: El tiempo de respuesta de `/ping` debe ser inferior a 100 ms bajo condiciones normales.
- RNF-3: **Tolerancia a Fallos**: Cero excepciones no controladas que provoquen la terminación del proceso principal de FastAPI/Uvicorn.

## Casos límite
- Meta tarda más de 10 segundos en responder a una petición de descarga de medios: La excepción de timeout se captura y se informa al usuario.
- Gemini experimenta alta latencia o rate limit: Se devuelve el mensaje de fallback en WhatsApp y se liberan todos los recursos temporales.
- Ráfaga simultánea de pings de monitoreo y mensajes de usuarios: `/ping` se ejecuta de forma asíncrona sin bloquear la recepción de webhooks.

## Fuera de alcance
- Escalado automático horizontal multirregión (limitado a la única instancia gratuita de Render).
- Almacenamiento persistente de logs en bases de datos externas de telemetría.

## Criterios de finalización
- Endpoint `GET /ping` implementado y probado con tests automatizados.
- Pruebas unitarias que simulen timeouts de `httpx` y llamadas a Gemini verificando la resiliencia del sistema.
- 100% de la suite de pruebas pasando en verde.
- Instrucciones de configuración en UptimeRobot documentadas y probadas.

## Dudas abiertas
- Ninguna. Cumple con los principios de bajo costo y alta disponibilidad de la constitución del proyecto.
