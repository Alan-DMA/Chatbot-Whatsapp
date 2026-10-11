import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "whatsapp-gemini-chatbot"}

@pytest.mark.asyncio
async def test_webhook_verification_success(monkeypatch):
    monkeypatch.setenv("VERIFY_TOKEN", "mi_token_secreto_123")
    from src.config import get_settings
    get_settings.cache_clear()

    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "mi_token_secreto_123",
        "hub.challenge": "1158201444"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/webhook", params=params)

    assert response.status_code == 200
    assert response.text == "1158201444"

@pytest.mark.asyncio
async def test_webhook_verification_invalid_token(monkeypatch):
    monkeypatch.setenv("VERIFY_TOKEN", "mi_token_secreto_123")
    from src.config import get_settings
    get_settings.cache_clear()

    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "token_falso_erroneo",
        "hub.challenge": "1158201444"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/webhook", params=params)

    assert response.status_code == 403
    assert response.json() == {"detail": "Verification token mismatch"}

@pytest.mark.asyncio
async def test_webhook_verification_missing_mode():
    params = {
        "hub.verify_token": "cualquier_token",
        "hub.challenge": "1158201444"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/webhook", params=params)

    assert response.status_code == 400
