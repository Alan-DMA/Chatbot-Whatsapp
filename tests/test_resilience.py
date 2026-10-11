import pytest
import httpx
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_ping_endpoint_instant_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

@pytest.mark.asyncio
async def test_webhook_resilient_to_meta_timeout():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "5491123456789",
                        "type": "text",
                        "text": {"body": "Hola"}
                    }]
                }
            }]
        }]
    }

    # Simular que enviar a Meta produce TimeoutException
    with patch("src.main.generate_gemini_text_response", new_callable=AsyncMock) as mock_gemini, \
         patch("src.main.send_whatsapp_text_message", new_callable=AsyncMock) as mock_send_wa:

        mock_gemini.return_value = "Hola, ¿cómo estás?"
        mock_send_wa.side_effect = httpx.TimeoutException("Meta API timeout")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/webhook", json=payload)

        # El servidor nunca debe caerse ante un timeout de Meta, debe devolver 200 OK
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
