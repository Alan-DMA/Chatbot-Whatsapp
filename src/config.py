import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    WHATSAPP_TOKEN: str = "default_wa_token"
    VERIFY_TOKEN: str = "default_verify_token"
    PHONE_NUMBER_ID: str = "default_phone_id"
    GEMINI_API_KEY: str = "default_gemini_key"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
