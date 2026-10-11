import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.services.gemini_service import generate_gemini_text_response

@pytest.mark.asyncio
async def test_generate_gemini_text_response_success(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()

    # Mock del SDK de Google GenAI
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hola! Soy Gemini y estoy listo para ayudarte."
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        response_text = await generate_gemini_text_response(
            prompt="Hola, ¿quién eres?",
            model="gemini-2.5-flash"
        )

        assert response_text == "Hola! Soy Gemini y estoy listo para ayudarte."
        mock_client.aio.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents="Hola, ¿quién eres?"
        )

@pytest.mark.asyncio
async def test_generate_gemini_text_response_fallback_on_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("API limit exceeded"))

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        response_text = await generate_gemini_text_response(
            prompt="Mensaje que causa error"
        )

        # Resiliencia: no debe colapsar, debe devolver mensaje amigable
        assert "Lo siento" in response_text or "disculpa" in response_text.lower()

@pytest.mark.asyncio
async def test_generate_gemini_multimodal_response_success(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()

    from src.services.gemini_service import generate_gemini_multimodal_response

    test_file = tmp_path / "test_audio.mp3"
    test_file.write_bytes(b"fake audio bytes")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Escuché tu nota de voz y entiendo tu mensaje."
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        result = await generate_gemini_multimodal_response(
            file_path=str(test_file),
            mime_type="audio/mp3",
            prompt="Por favor transcribe o responde a este audio."
        )

        assert result == "Escuché tu nota de voz y entiendo tu mensaje."
        mock_client.aio.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_generate_gemini_image_success(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.gemini_service import generate_gemini_image

    mock_client = MagicMock()
    mock_img_obj = MagicMock()
    mock_img_obj.image.image_bytes = b"fake_jpeg_image_bytes"
    mock_response = MagicMock()
    mock_response.generated_images = [mock_img_obj]
    mock_client.aio.models.generate_images = AsyncMock(return_value=mock_response)

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        img_bytes = await generate_gemini_image(prompt="a cute astronaut cat in space")
        assert img_bytes == b"fake_jpeg_image_bytes"
        mock_client.aio.models.generate_images.assert_called_once()

@pytest.mark.asyncio
async def test_generate_gemini_image_error_raises(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.gemini_service import generate_gemini_image

    mock_client = MagicMock()
    mock_client.aio.models.generate_images = AsyncMock(side_effect=Exception("Safety filter triggered"))

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        with pytest.raises(Exception):
            await generate_gemini_image(prompt="unsafe prompt")

@pytest.mark.asyncio
async def test_process_user_message_intent_image_request(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.gemini_service import process_user_message_intent

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"generate_image": true, "image_prompt": "a red sports car on Mars", "caption": "¡Aquí tienes tu coche en Marte! 🚗"}'
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        intent = await process_user_message_intent(text="Dibuja un coche rojo en Marte")
        assert intent["generate_image"] is True
        assert intent["image_prompt"] == "a red sports car on Mars"
        assert "¡Aquí tienes tu coche en Marte!" in intent["caption"]

@pytest.mark.asyncio
async def test_process_user_message_intent_chat_message(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.gemini_service import process_user_message_intent

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"generate_image": false, "reply": "¡Hola! ¿En qué puedo ayudarte hoy?"}'
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        intent = await process_user_message_intent(text="Hola buenos días")
        assert intent["generate_image"] is False
        assert intent["reply"] == "¡Hola! ¿En qué puedo ayudarte hoy?"

@pytest.mark.asyncio
async def test_process_user_message_intent_fallback_on_invalid_json(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.gemini_service import process_user_message_intent

    mock_client = MagicMock()
    mock_response = MagicMock()
    # Respuesta no JSON (texto plano)
    mock_response.text = "Claro, puedo ayudarte con cualquier consulta que tengas."
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        intent = await process_user_message_intent(text="Ayuda por favor")
        assert intent["generate_image"] is False
        assert intent["reply"] == "Claro, puedo ayudarte con cualquier consulta que tengas."

@pytest.mark.asyncio
async def test_process_user_message_intent_with_history(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_api_key_123")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.gemini_service import process_user_message_intent

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"generate_image": true, "image_prompt": "a dog in space", "caption": "¡Aquí tienes la opción 2! 🐶"}'
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    history = [
        {"role": "user", "content": "Dame opciones para dibujar"},
        {"role": "model", "content": "1. Gato astronauta. 2. Perro espacial."}
    ]

    with patch("src.services.gemini_service.get_genai_client", return_value=mock_client):
        intent = await process_user_message_intent(text="La opción 2", history=history)
        assert intent["generate_image"] is True
        assert intent["image_prompt"] == "a dog in space"

        # Verificar que el historial se incluyó en la llamada a Gemini
        call_kwargs = mock_client.aio.models.generate_content.call_args[1]
        sent_contents = call_kwargs["contents"]
        assert "Gato astronauta" in sent_contents
        assert "Perro espacial" in sent_contents
        assert "La opción 2" in sent_contents

