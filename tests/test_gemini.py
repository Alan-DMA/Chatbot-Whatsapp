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

