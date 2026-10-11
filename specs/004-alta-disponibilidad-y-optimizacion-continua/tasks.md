# Tareas — Spec 004: Alta Disponibilidad y Optimización Continua

- [x] **T1. Implementación de endpoint secundario /ping.** RF-1, RF-2
  - Hecho cuando: Exista ruta `GET /ping` respondiendo `200 OK` con `{"status": "alive"}` y su prueba unitaria esté en verde.
- [x] **T2. Blindaje de timeouts y manejo resiliente de excepciones externas.** RF-3, RF-4, RNF-3
  - Hecho cuando: Las llamadas hacia Meta y Gemini cuenten con captura explícita de `httpx.TimeoutException` y caídas de conexión, con tests automatizados simulando fallos de red pasando al 100%.
- [x] **T3. Despliegue en Render y configuración de monitor en UptimeRobot.** RF-5, RNF-1
  - Hecho cuando: Los cambios estén en GitHub/Render, el monitor en UptimeRobot esté activo enviando pings cada 14 minutos a `https://chatbot-whatsapp-614d.onrender.com/health` o `/ping`, y `MEMORY.md` quede actualizado.
