import pytest
import httpx
from unittest.mock import AsyncMock, patch
from src.services.whatsapp_service import send_whatsapp_text_message

@pytest.mark.asyncio
async def test_send_whatsapp_text_message_success(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "fake_token_123")
    monkeypatch.setenv("PHONE_NUMBER_ID", "10987654321")
    from src.config import get_settings
    get_settings.cache_clear()

    dummy_request = httpx.Request("POST", "https://graph.facebook.com/v21.0/10987654321/messages")
    mock_response = httpx.Response(
        status_code=200,
        json={"messaging_product": "whatsapp", "messages": [{"id": "wamid.HBgL..."}]},
        request=dummy_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await send_whatsapp_text_message(
            to_phone_number="123456789",
            text="Hola, soy tu chatbot"
        )

        assert result["messages"][0]["id"] == "wamid.HBgL..."
        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args

        # Validar URL esperada de WhatsApp Cloud API v21.0
        assert "https://graph.facebook.com/v21.0/10987654321/messages" in call_args[0]

        # Validar headers
        assert call_kwargs["headers"]["Authorization"] == "Bearer fake_token_123"
        assert call_kwargs["headers"]["Content-Type"] == "application/json"

        # Validar payload de Meta
        payload = call_kwargs["json"]
        assert payload["messaging_product"] == "whatsapp"
        assert payload["recipient_type"] == "individual"
        assert payload["to"] == "123456789"
        assert payload["type"] == "text"
        assert payload["text"]["body"] == "Hola, soy tu chatbot"

@pytest.mark.asyncio
async def test_send_whatsapp_text_message_api_error(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "fake_token_123")
    monkeypatch.setenv("PHONE_NUMBER_ID", "10987654321")
    from src.config import get_settings
    get_settings.cache_clear()

    dummy_request = httpx.Request("POST", "https://graph.facebook.com/v21.0/10987654321/messages")
    mock_response = httpx.Response(
        status_code=400,
        json={"error": {"message": "Invalid OAuth access token", "type": "OAuthException"}},
        request=dummy_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await send_whatsapp_text_message(
                to_phone_number="123456789",
                text="Mensaje con error"
            )

@pytest.mark.asyncio
async def test_upload_media_file_success(tmp_path, monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "fake_token_123")
    monkeypatch.setenv("PHONE_NUMBER_ID", "10987654321")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.whatsapp_service import upload_media_file

    dummy_file = tmp_path / "voice.ogg"
    dummy_file.write_bytes(b"dummy ogg bytes")

    dummy_request = httpx.Request("POST", "https://graph.facebook.com/v21.0/10987654321/media")
    mock_response = httpx.Response(
        status_code=200,
        json={"id": "media_uploaded_999"},
        request=dummy_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        media_id = await upload_media_file(str(dummy_file))
        assert media_id == "media_uploaded_999"
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_send_whatsapp_audio_message_success(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "fake_token_123")
    monkeypatch.setenv("PHONE_NUMBER_ID", "10987654321")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.whatsapp_service import send_whatsapp_audio_message

    dummy_request = httpx.Request("POST", "https://graph.facebook.com/v21.0/10987654321/messages")
    mock_response = httpx.Response(
        status_code=200,
        json={"messages": [{"id": "wamid.audio123"}]},
        request=dummy_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await send_whatsapp_audio_message(to_phone_number="123456789", media_id="media_uploaded_999")
        assert res["messages"][0]["id"] == "wamid.audio123"
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["type"] == "audio"
        assert call_kwargs["json"]["audio"]["id"] == "media_uploaded_999"

@pytest.mark.asyncio
async def test_send_whatsapp_image_message_success(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "fake_token_123")
    monkeypatch.setenv("PHONE_NUMBER_ID", "10987654321")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.whatsapp_service import send_whatsapp_image_message

    dummy_request = httpx.Request("POST", "https://graph.facebook.com/v21.0/10987654321/messages")
    mock_response = httpx.Response(
        status_code=200,
        json={"messages": [{"id": "wamid.img123"}]},
        request=dummy_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await send_whatsapp_image_message(
            to_phone_number="123456789",
            media_id="media_img_999",
            caption="Aquí tienes tu imagen"
        )
        assert res["messages"][0]["id"] == "wamid.img123"
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["type"] == "image"
        assert call_kwargs["json"]["image"]["id"] == "media_img_999"
        assert call_kwargs["json"]["image"]["caption"] == "Aquí tienes tu imagen"

@pytest.mark.asyncio
async def test_send_whatsapp_image_message_without_caption(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "fake_token_123")
    monkeypatch.setenv("PHONE_NUMBER_ID", "10987654321")
    from src.config import get_settings
    get_settings.cache_clear()
    from src.services.whatsapp_service import send_whatsapp_image_message

    dummy_request = httpx.Request("POST", "https://graph.facebook.com/v21.0/10987654321/messages")
    mock_response = httpx.Response(
        status_code=200,
        json={"messages": [{"id": "wamid.img124"}]},
        request=dummy_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await send_whatsapp_image_message(
            to_phone_number="123456789",
            media_id="media_img_999"
        )
        assert res["messages"][0]["id"] == "wamid.img124"
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["type"] == "image"
        assert call_kwargs["json"]["image"]["id"] == "media_img_999"
        assert "caption" not in call_kwargs["json"]["image"]

