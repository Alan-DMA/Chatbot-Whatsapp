# Plan Técnico — Spec 004: Alta Disponibilidad y Optimización Continua

## Archivos y responsabilidades
- `src/main.py`:
  - Agregar endpoint `GET /ping` con respuesta instantánea `{"status": "alive"}` y código HTTP 200 OK.
  - Blindar el flujo de mensajes en `POST /webhook` capturando explícitamente `httpx.TimeoutException`, `httpx.NetworkError` y excepciones generales con fallback automático al usuario.
- `src/services/whatsapp_service.py`:
  - Configurar timeouts defensivos estructurados en las peticiones HTTP a Meta Graph API (`timeout=httpx.Timeout(10.0, connect=5.0)`).
- `src/services/gemini_service.py`:
  - Manejo de timeout e interrupciones en las llamadas asíncronas de Google GenAI SDK con mensajes claros de respaldo.
- `tests/test_resilience.py`:
  - Pruebas automatizadas para verificar que `/ping` responda 200 OK.
  - Pruebas simulando timeouts de red con Meta y Google verificando que el servidor responda 200 al webhook y devuelva el mensaje de respaldo.

## Decisiones justificadas
1. **Ruta `/ping` ultraligera:** No debe cargar dependencias pesadas, ni leer bases de datos, ni consultar APIs externas. Solo retorna un diccionario estático para garantizar latencias < 50ms aptas para monitores concurrentes.
2. **Defensa en profundidad en timeouts:** Los webhooks de Meta tienen un límite estricto de 3-5 segundos. Aunque el endpoint responde 200 inmediatamente antes del procesamiento en segundo plano, las tareas en background deben tener timeouts explícitos para no colgar workers de asyncio.
3. **Persistencia 24/7:** UptimeRobot envía peticiones cada 14 min a `/ping`, reiniciando el temporizador de 15 min de inactividad de Render.
