import os
import sqlite3
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.path.join("data", "history.db")

RESET_COMMANDS = {
    "/reset",
    "reset",
    "reiniciar",
    "reiniciar conversación",
    "reiniciar conversacion",
    "olvida la conversación",
    "olvida la conversacion",
    "nueva conversación",
    "nueva conversacion",
    "borrar memoria",
    "borrar historial",
}

def get_db_path(db_path: Optional[str] = None) -> str:
    path = db_path or DEFAULT_DB_PATH
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    return path

def init_history_db(db_path: Optional[str] = None) -> None:
    """Inicializa la base de datos y la tabla de historial si no existen."""
    target_path = get_db_path(db_path)
    try:
        with sqlite3.connect(target_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_phone_number ON conversation_history(phone_number);
            """)
            conn.commit()
    except Exception as exc:
        logger.error(f"Error inicializando la base de datos de historial ({target_path}): {exc}", exc_info=True)

def is_reset_command(text: str) -> bool:
    """Comprueba si el texto enviado corresponde a un comando explícito de reinicio."""
    if not text:
        return False
    normalized = text.strip().lower()
    return normalized in RESET_COMMANDS

def get_conversation_history(
    phone_number: str,
    max_turns: int = 10,
    ttl_minutes: int = 45,
    db_path: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Recupera el historial activo de un usuario en orden cronológico.
    Aplica verificación de TTL (expiración por inactividad) y ventana deslizante.
    """
    if not phone_number:
        return []

    target_path = get_db_path(db_path)
    try:
        with sqlite3.connect(target_path) as conn:
            cursor = conn.cursor()

            # 1. Verificar si hay mensajes y si expiraron por TTL
            cursor.execute("""
                SELECT COUNT(*) FROM conversation_history WHERE phone_number = ?
            """, (phone_number,))
            total_count = cursor.fetchone()[0]

            if total_count == 0:
                return []

            cursor.execute("""
                SELECT COUNT(*) FROM conversation_history
                WHERE phone_number = ? AND created_at >= datetime('now', ? || ' minutes')
            """, (phone_number, f"-{ttl_minutes}"))
            active_count = cursor.fetchone()[0]

            if active_count == 0:
                # Todos los mensajes son más antiguos que el TTL: purgar historial
                cursor.execute("DELETE FROM conversation_history WHERE phone_number = ?", (phone_number,))
                conn.commit()
                return []

            # 2. Recuperar últimos N mensajes (max_turns * 2) en orden cronológico
            limit = max_turns * 2
            cursor.execute("""
                SELECT role, content FROM (
                    SELECT id, role, content FROM conversation_history
                    WHERE phone_number = ?
                    ORDER BY id DESC
                    LIMIT ?
                ) ORDER BY id ASC
            """, (phone_number, limit))

            rows = cursor.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]
    except Exception as exc:
        logger.error(f"Error consultando historial para {phone_number}: {exc}", exc_info=True)
        return []

def add_conversation_turn(
    phone_number: str,
    user_message: str,
    model_response: str,
    max_turns: int = 10,
    db_path: Optional[str] = None
) -> None:
    """
    Registra un turno completo (mensaje del usuario y respuesta de la IA).
    Poda automáticamente los turnos que excedan la ventana deslizante permitida.
    """
    if not phone_number or not user_message or not model_response:
        return

    target_path = get_db_path(db_path)
    try:
        with sqlite3.connect(target_path) as conn:
            cursor = conn.cursor()

            # Insertar turno
            cursor.execute("""
                INSERT INTO conversation_history (phone_number, role, content, created_at)
                VALUES (?, 'user', ?, datetime('now'))
            """, (phone_number, user_message.strip()))

            cursor.execute("""
                INSERT INTO conversation_history (phone_number, role, content, created_at)
                VALUES (?, 'model', ?, datetime('now'))
            """, (phone_number, model_response.strip()))

            # Podar ventana deslizante (conservar solo los últimos max_turns * 2 mensajes)
            limit = max_turns * 2
            cursor.execute("""
                DELETE FROM conversation_history
                WHERE phone_number = ? AND id NOT IN (
                    SELECT id FROM conversation_history
                    WHERE phone_number = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
            """, (phone_number, phone_number, limit))

            conn.commit()
    except Exception as exc:
        logger.error(f"Error guardando turno en historial para {phone_number}: {exc}", exc_info=True)

def clear_conversation_history(
    phone_number: str,
    db_path: Optional[str] = None
) -> None:
    """Elimina completamente el historial conversacional asociado al número de teléfono."""
    if not phone_number:
        return

    target_path = get_db_path(db_path)
    try:
        with sqlite3.connect(target_path) as conn:
            conn.execute("DELETE FROM conversation_history WHERE phone_number = ?", (phone_number,))
            conn.commit()
    except Exception as exc:
        logger.error(f"Error limpiando historial para {phone_number}: {exc}", exc_info=True)
