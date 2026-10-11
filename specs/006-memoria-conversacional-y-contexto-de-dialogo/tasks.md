# Tareas — Spec 006: Memoria Conversacional y Contexto de Diálogo

- [x] **T1. Capa de datos y servicio `history_service.py` con tests unitarios.** RF-1, RF-2, RF-4, RF-5, RF-6, RF-7
  - Hecho cuando: `init_history_db`, `get_conversation_history`, `add_conversation_turn`, `clear_conversation_history` e `is_reset_command` funcionan correctamente, aplican TTL y ventana deslizante, y pasan sus tests unitarios en `tests/test_history_service.py`.

- [x] **T2. Inyección de contexto conversacional en `gemini_service.py` con tests.** RF-3
  - Hecho cuando: `process_user_message_intent` recibe el historial acumulado, lo formatea en el contexto enviado a Gemini y pasa sus tests en `tests/test_gemini.py`.

- [x] **T3. Integración de memoria y comando de reinicio en `src/main.py` con tests.** RF-1, RF-4, RF-6
  - Hecho cuando: `POST /webhook` atiende comandos de reinicio (`/reset`), recupera el historial de la sesión, lo envía a Gemini y almacena cada nuevo turno resultante, pasando sus tests en `tests/test_webhook_receiver.py`.

- [x] **T4. Verificación integral de la suite de tests (`pytest`) y despliegue a producción.** Criterios de finalización
  - Hecho cuando: Toda la suite de tests pasa al 100% en verde, se actualiza `MEMORY.md` y se despliega a Render.
