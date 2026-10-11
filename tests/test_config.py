import os
import pytest
from src.config import Settings, get_settings

def test_settings_default_and_types():
    settings = Settings(
        WHATSAPP_TOKEN="test_wa_token",
        VERIFY_TOKEN="test_verify_token",
        PHONE_NUMBER_ID="1234567890",
        GEMINI_API_KEY="test_gemini_key",
    )
    assert settings.WHATSAPP_TOKEN == "test_wa_token"
    assert settings.VERIFY_TOKEN == "test_verify_token"
    assert settings.PHONE_NUMBER_ID == "1234567890"
    assert settings.GEMINI_API_KEY == "test_gemini_key"
    assert settings.PORT == 8000
    assert settings.HOST == "0.0.0.0"

def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "env_wa_token")
    monkeypatch.setenv("VERIFY_TOKEN", "env_verify_token")
    monkeypatch.setenv("PHONE_NUMBER_ID", "9876543210")
    monkeypatch.setenv("GEMINI_API_KEY", "env_gemini_key")
    monkeypatch.setenv("PORT", "9000")

    settings = get_settings()
    assert settings.WHATSAPP_TOKEN == "env_wa_token"
    assert settings.VERIFY_TOKEN == "env_verify_token"
    assert settings.PHONE_NUMBER_ID == "9876543210"
    assert settings.GEMINI_API_KEY == "env_gemini_key"
    assert settings.PORT == 9000
