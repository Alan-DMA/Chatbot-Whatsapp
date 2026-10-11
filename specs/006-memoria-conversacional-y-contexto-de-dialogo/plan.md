# Plan Técnico — Spec 006: Memoria Conversacional y Contexto de Diálogo

## 1. Archivos y responsabilidades
- `src/services/history_service.py`:
  - Capa de datos y lógica de historial en SQLite local (`data/history.db`).
  - Funciones de inicialización de esquema, consulta con TTL y ventana deslizante, inserción de turnos, y borrado/reinicio. (Cubre RF-1, RF-2, RF-4, RF-5, RF-6, RF-7, RNF-1, RNF-2, RNF-3).
- `src/services/gemini_service.py`:
  - Extender `process_user_message_intent(text: str, history: Optional[List[Dict[str, str]]] = None)` para formatear e inyectar el historial en el contexto enviado a Gemini. (Cubre RF-3).
- `src/main.py`:
  - Orquestar la verificación de comandos de reinicio (`/reset`), recuperación de historial, despacho a Gemini y almacenamiento del turno resultante en `POST /webhook`. (Cubre RF-1, RF-4, RF-6).
- `tests/test_history_service.py`:
  - Pruebas unitarias de aislamiento por usuario, TTL, ventana deslizante, comandos de reinicio y tolerancia a fallos.
- `tests/test_gemini.py` & `tests/test_webhook_receiver.py`:
  - Pruebas de integración verificando la inyección de contexto y persistencia de turnos.

## 2. Interfaz y tipos
```python
# src/services/history_service.py
from typing import List, Dict, Optional

def init_history_db(db_path: Optional[str] = None) -> None: ...

def get_conversation_history(
    phone_number: str,
    max_turns: int = 10,
    ttl_minutes: int = 45,
    db_path: Optional[str] = None
) -> List[Dict[str, str]]: ...

def add_conversation_turn(
    phone_number: str,
    user_message: str,
    model_response: str,
    max_turns: int = 10,
    db_path: Optional[str] = None
) -> None: ...

def clear_conversation_history(
    phone_number: str,
    db_path: Optional[str] = None
) -> None: ...

def is_reset_command(text: str) -> bool: ...
```

## 3. Algoritmo en pseudocódigo
```text
CUANDO llega mensaje de texto o audio (texto_usuario, telefono):
  SI is_reset_command(texto_usuario):
    clear_conversation_history(telefono)
    enviar_mensaje(telefono, "¡Listo! He reiniciado nuestra conversación...")
    RETORNAR

  historial = get_conversation_history(telefono, max_turns=10, ttl_minutes=45)
  intención = process_user_message_intent(texto_usuario, history=historial)

  SI intención["generate_image"]:
    generar y enviar imagen con caption
    add_conversation_turn(telefono, texto_usuario, intención["caption"])
  SINO:
    enviar mensaje de texto con respuesta
    add_conversation_turn(telefono, texto_usuario, intención["reply"])
```

## 4. Decisiones justificadas
1. **SQLite local con creación automática de directorio `data/`:**
   - *Alternativa descartada:* Diccionario en memoria sin persistencia o Redis externo.
   - *Razón:* SQLite viene integrado en la biblioteca estándar de Python (cero librerías adicionales), ofrece latencia sub-milisegundo, no requiere credenciales de servicios de terceros y persiste entre peticiones dentro del contenedor.
2. **Formateo de historial en contexto textual estructurado:**
   - *Alternativa descartada:* Manejo complejo de objetos ChatSession con estado mutante en memoria.
   - *Razón:* `process_user_message_intent` resuelve en una única llamada la intención de imagen o respuesta textual. Incluir el historial de turnos cronológicos directamente en el prompt permite que Gemini razone sobre referencias pasadas (como "¿cuál era la segunda opción?") de forma totalmente declarativa y sin riesgo de desincronización de hilos.

## 5. Estrategia de tests
- Tests unitarios en `tests/test_history_service.py` usando bases de datos temporales (`tmp_path / "test.db"`).
- Pruebas de expiración TTL manipulando marcas de tiempo.
- Pruebas de ventana deslizante insertando más turnos que el límite.
- Ejecución con `pytest`.
