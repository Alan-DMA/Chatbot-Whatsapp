# AGENTS.md — Chatbot Multimodal para WhatsApp

Chatbot automatizado para WhatsApp capaz de procesar mensajes de texto, notas de voz e imágenes con la API de Google (Gemini) y WhatsApp Cloud API, desplegado 24/7 en Render (Free Tier).

## Stack y estructura
- **Lenguaje y framework:** Python 3.11+, FastAPI (o Flask) para endpoints webhooks y healthcheck.
- **Mensajería:** Meta WhatsApp Cloud API (Webhooks entrantes y peticiones POST de salida).
- **IA:** Google GenAI SDK (Gemini multimodal para texto, visión y audio).
- **Procesamiento de audio:** binario del sistema `ffmpeg` para transcodificación `.ogg` (Opus) -> formatos estándar procesables por Gemini.
- **Contenerización y despliegue:** Docker (`Dockerfile`), Render (Web Service), UptimeRobot (pings cada 14 min a `/health` o `/ping`).
- **Estructura:**
  - `agents/`: Subagentes SDD (`coordinator.md`, `planner.md`, `implementer.md`, `reviewer.md`).
  - `docs/constitution.md`: Principios inmutables del proyecto.
  - `specs/`: Especificaciones por funcionalidad (`specs/NNN-nombre/`).
  - `tests/`: Pruebas automatizadas (pytest).
  - `src/` (o raíz): Aplicación Python, clientes de API y utilidades de medios.

## Comandos
- Crear entorno virtual: `python -m venv .venv` y `.venv\Scripts\activate`
- Instalar dependencias: `pip install -r requirements.txt`
- Ejecutar servidor local: `uvicorn src.main:app --reload --port 8000`
- Tests: `pytest`
- Crear nueva spec: `sdd spec <nombre>`
- Listar specs: `sdd list`
- Construir contenedor Docker: `docker build -t whatsapp-chatbot .`

## Convenciones
- Código en Python idiomático (PEP 8), tipado estricto con `pydantic` o type hints.
- Mensajes y logs en español/inglés claros y estructurados sin exponer credenciales ni números de teléfono sensibles.
- Rutas del webhook: `GET /webhook` (verificación de token de Meta) y `POST /webhook` (recepción de eventos).
- Ruta de disponibilidad: `GET /health` o `GET /ping` para UptimeRobot.

## Reglas de dominio / trampas conocidas
- **Purgar almacenamiento temporal:** WhatsApp envía audios e imágenes que deben descargarse para transcodificar/analizar. El contenedor de Render tiene almacenamiento efímero y limitado; es OBLIGATORIO eliminar archivos temporales (`os.remove`) inmediatamente después de enviarlos a Gemini.
- **Audio Opus en WhatsApp:** Las notas de voz vienen encapsuladas en contenedores OGG/Opus. `ffmpeg` es un requerimiento indispensable a nivel de sistema dentro del `Dockerfile`.
- **Modo Sleep de Render:** Render apaga la instancia tras 15 minutos sin tráfico entrante. El endpoint `/health` debe responder con `200 OK` rápidamente sin cargar dependencias pesadas para que UptimeRobot lo mantenga activo.
- **Validación del Webhook de Meta:** Responder con el `hub.challenge` como texto plano (no JSON) cuando el `hub.verify_token` coincida.

## Reglas
- Lee `docs/constitution.md` y la spec activa (`specs/NNN-*/`) antes de tocar código.
- Seguir estrictamente el flujo SDD: Spec -> Plan -> Tareas -> Implementación (con tests) -> Verificación.

## Forma de trabajar
- Planificar antes de tocar código; trabajar en tareas pequeñas (máximo 1 tarea a la vez).
- En cada cambio de código, verificar con tests automatizados.

## Memoria
- Al empezar, lee `MEMORY.md` para conocer el estado del proyecto y las decisiones tomadas.
- Al terminar una tarea, actualízalo: estado actual, decisiones importantes (con su porqué) y errores a evitar.
- Mantenlo breve (máximo ~50 líneas): resume o elimina lo que ya no aporte.
- Si algo se convierte en una regla permanente, propón moverlo a `AGENTS.md` en lugar de dejarlo en la memoria.
- No guardes nunca datos sensibles (claves, tokens, datos personales).

## Límites
- ✅ Siempre: actualizar `MEMORY.md` al terminar cada tarea.
- ⚠️ Pregunta antes: dependencias nuevas, cambios de arquitectura en el pipeline multimodal, variables de entorno.
- 🚫 Nunca: subir secretos (tokens de WhatsApp, API keys de Gemini, verify tokens) al repositorio ni dejar archivos multimedia temporales sin borrar.

## Verificación
- Tests de endpoints con `pytest`.
- Verificación de simulación del payload del webhook de Meta (texto, audio, imagen).
- Prueba local de healthcheck `/health`.
