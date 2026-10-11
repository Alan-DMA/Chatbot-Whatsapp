import time
import sqlite3
import pytest
from src.services.history_service import (
    init_history_db,
    get_conversation_history,
    add_conversation_turn,
    clear_conversation_history,
    is_reset_command,
)

def test_init_and_add_turn(tmp_path):
    db_file = str(tmp_path / "test_history.db")
    init_history_db(db_path=db_file)

    add_conversation_turn(
        phone_number="12345",
        user_message="Hola",
        model_response="¡Hola! ¿Cómo estás?",
        db_path=db_file
    )

    history = get_conversation_history(phone_number="12345", db_path=db_file)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hola"
    assert history[1]["role"] == "model"
    assert history[1]["content"] == "¡Hola! ¿Cómo estás?"

def test_user_isolation(tmp_path):
    db_file = str(tmp_path / "test_history.db")
    init_history_db(db_path=db_file)

    add_conversation_turn(phone_number="111", user_message="Mensaje de 111", model_response="Respuesta a 111", db_path=db_file)
    add_conversation_turn(phone_number="222", user_message="Mensaje de 222", model_response="Respuesta a 222", db_path=db_file)

    history_111 = get_conversation_history(phone_number="111", db_path=db_file)
    history_222 = get_conversation_history(phone_number="222", db_path=db_file)

    assert len(history_111) == 2
    assert history_111[0]["content"] == "Mensaje de 111"

    assert len(history_222) == 2
    assert history_222[0]["content"] == "Mensaje de 222"

def test_sliding_window(tmp_path):
    db_file = str(tmp_path / "test_history.db")
    init_history_db(db_path=db_file)

    # Insertar 4 turnos con max_turns=2
    for i in range(1, 5):
        add_conversation_turn(
            phone_number="12345",
            user_message=f"Mensaje {i}",
            model_response=f"Respuesta {i}",
            max_turns=2,
            db_path=db_file
        )

    history = get_conversation_history(phone_number="12345", max_turns=2, db_path=db_file)
    # Deben quedar exactamente los últimos 2 turnos (4 mensajes: Turno 3 y Turno 4)
    assert len(history) == 4
    assert history[0]["content"] == "Mensaje 3"
    assert history[1]["content"] == "Respuesta 3"
    assert history[2]["content"] == "Mensaje 4"
    assert history[3]["content"] == "Respuesta 4"

def test_ttl_expiration(tmp_path):
    db_file = str(tmp_path / "test_history.db")
    init_history_db(db_path=db_file)

    add_conversation_turn(
        phone_number="12345",
        user_message="Mensaje viejo",
        model_response="Respuesta vieja",
        db_path=db_file
    )

    # Simular que el mensaje fue insertado hace 60 minutos
    with sqlite3.connect(db_file) as conn:
        conn.execute("UPDATE conversation_history SET created_at = datetime('now', '-60 minutes') WHERE phone_number = '12345'")
        conn.commit()

    # Con TTL de 30 minutos, debe expirar y retornar lista vacía
    history = get_conversation_history(phone_number="12345", ttl_minutes=30, db_path=db_file)
    assert len(history) == 0

def test_clear_conversation_history(tmp_path):
    db_file = str(tmp_path / "test_history.db")
    init_history_db(db_path=db_file)

    add_conversation_turn(phone_number="12345", user_message="Hola", model_response="Hola", db_path=db_file)
    clear_conversation_history(phone_number="12345", db_path=db_file)

    history = get_conversation_history(phone_number="12345", db_path=db_file)
    assert len(history) == 0

def test_is_reset_command():
    assert is_reset_command("/reset") is True
    assert is_reset_command("  /RESET  ") is True
    assert is_reset_command("reiniciar conversación") is True
    assert is_reset_command("olvida la conversación") is True
    assert is_reset_command("Hola, ¿cómo estás?") is False
    assert is_reset_command("Dame 2 opciones") is False
