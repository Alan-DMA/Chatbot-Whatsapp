import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from src.main import app

# Payload típico que envía Meta al recibir un mensaje de texto
META_TEXT_MESSAGE_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "100200300400",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15550234567",
                            "phone_number_id": "10987654321"
                        },
                        "contacts": [
                            {
                                "profile": {"name": "Usuario Prueba"},
                                "wa_id": "5491123456789"
                            }
                        ],
                        "messages": [
                            {
                                "from": "5491123456789",
                                "id": "wamid.HBgLM...",
                                "timestamp": "1728500000",
                                "text": {
                                    "body": "¿Cómo estás hoy?"
                                },
                                "type": "text"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

# Payload típico de actualización de estado (sent, delivered, read)
META_STATUS_UPDATE_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "100200300400",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15550234567",
                            "phone_number_id": "10987654321"
                        },
                        "statuses": [
                            {
                                "id": "wamid.HBgLM...",
                                "status": "delivered",
                                "timestamp": "1728500010",
                                "recipient_id": "5491123456789"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

@pytest.mark.asyncio
async def test_webhook_post_text_message_end_to_end():
    with patch("src.main.generate_gemini_text_response", new_callable=AsyncMock) as mock_gemini, \
         patch("src.main.send_whatsapp_text_message", new_callable=AsyncMock) as mock_send_whatsapp:

        mock_gemini.return_value = "Estoy muy bien, gracias por preguntar."
        mock_send_whatsapp.return_value = {"messages": [{"id": "wamid.resp..."}]}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/webhook", json=META_TEXT_MESSAGE_PAYLOAD)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # Verificar que se extrajo el mensaje y se llamó a Gemini
        mock_gemini.assert_called_once_with(prompt="¿Cómo estás hoy?")

        # Verificar que la respuesta de Gemini se envió al destinatario correcto
        mock_send_whatsapp.assert_called_once_with(
            to_phone_number="5491123456789",
            text="Estoy muy bien, gracias por preguntar."
        )

@pytest.mark.asyncio
async def test_webhook_post_status_update_ignored():
    with patch("src.main.generate_gemini_text_response", new_callable=AsyncMock) as mock_gemini, \
         patch("src.main.send_whatsapp_text_message", new_callable=AsyncMock) as mock_send_whatsapp:

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/webhook", json=META_STATUS_UPDATE_PAYLOAD)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # No debe invocar ni Gemini ni enviar mensajes en eventos de estado
        mock_gemini.assert_not_called()
        mock_send_whatsapp.assert_not_called()

@pytest.mark.asyncio
async def test_webhook_post_empty_or_unsupported_event():
    empty_payload = {"object": "whatsapp_business_account", "entry": []}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhook", json=empty_payload)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

META_IMAGE_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "100200300400",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "messages": [{
                    "from": "5491123456789",
                    "id": "wamid.img1",
                    "type": "image",
                    "image": {
                        "id": "media_img_123",
                        "mime_type": "image/jpeg",
                        "caption": "¿Qué animal es este?"
                    }
                }]
            },
            "field": "messages"
        }]
    }]
}

META_AUDIO_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "100200300400",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "messages": [{
                    "from": "5491123456789",
                    "id": "wamid.aud1",
                    "type": "audio",
                    "audio": {
                        "id": "media_aud_123",
                        "mime_type": "audio/ogg; codecs=opus"
                    }
                }]
            },
            "field": "messages"
        }]
    }]
}

@pytest.mark.asyncio
async def test_webhook_post_image_message_success(tmp_path):
    with patch("src.main.get_media_url", new_callable=AsyncMock) as mock_get_media, \
         patch("src.main.download_media_file", new_callable=AsyncMock) as mock_download, \
         patch("src.main.generate_gemini_multimodal_response", new_callable=AsyncMock) as mock_gemini_mm, \
         patch("src.main.send_whatsapp_text_message", new_callable=AsyncMock) as mock_send_wa, \
         patch("src.main.cleanup_files") as mock_cleanup:

        mock_get_media.return_value = {"url": "https://media.url/img", "mime_type": "image/jpeg"}
        mock_download.return_value = str(tmp_path / "img.jpg")
        mock_gemini_mm.return_value = "Es un gato siamés."

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/webhook", json=META_IMAGE_PAYLOAD)

        assert response.status_code == 200
        mock_get_media.assert_called_once_with(media_id="media_img_123")
        mock_gemini_mm.assert_called_once()
        mock_send_wa.assert_called_once_with(to_phone_number="5491123456789", text="Es un gato siamés.")
        mock_cleanup.assert_called_once()

@pytest.mark.asyncio
async def test_webhook_post_audio_message_success(tmp_path):
    with patch("src.main.get_media_url", new_callable=AsyncMock) as mock_get_media, \
         patch("src.main.download_media_file", new_callable=AsyncMock) as mock_download, \
         patch("src.main.convert_ogg_to_mp3") as mock_convert_mp3, \
         patch("src.main.generate_gemini_multimodal_response", new_callable=AsyncMock) as mock_gemini_mm, \
         patch("src.main.convert_text_to_whatsapp_voice_note") as mock_tts, \
         patch("src.main.upload_media_file", new_callable=AsyncMock) as mock_upload, \
         patch("src.main.send_whatsapp_audio_message", new_callable=AsyncMock) as mock_send_audio, \
         patch("src.main.cleanup_files") as mock_cleanup:

        mock_get_media.return_value = {"url": "https://media.url/aud", "mime_type": "audio/ogg; codecs=opus"}
        mock_download.return_value = str(tmp_path / "voice.ogg")
        mock_convert_mp3.return_value = str(tmp_path / "voice.mp3")
        mock_gemini_mm.return_value = "Hola, escuché tu audio perfectamente."
        mock_tts.return_value = str(tmp_path / "reply.ogg")
        mock_upload.return_value = "media_reply_999"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/webhook", json=META_AUDIO_PAYLOAD)

        assert response.status_code == 200
        mock_get_media.assert_called_once_with(media_id="media_aud_123")
        mock_convert_mp3.assert_called_once()
        mock_gemini_mm.assert_called_once()
        mock_tts.assert_called_once()
        mock_upload.assert_called_once()
        mock_send_audio.assert_called_once_with(to_phone_number="5491123456789", media_id="media_reply_999")
        mock_cleanup.assert_called_once()

