from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    APP_NAME: str = "ASC Chatbot"
    ENV: str = "development"
    SECRET_KEY: str
    DEBUG: bool = False

    DATABASE_URL: str

    WHATSAPP_API_URL: str
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_VERIFY_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str

    ADMIN_USERNAME: str
    ADMIN_PASSWORD_HASH: str

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"

    MEDIA_ROOT: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

    DEFAULT_LANGUAGE: str = "en"
    FALLBACK_REPLY: str = "Sorry, I didn't understand that."

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()