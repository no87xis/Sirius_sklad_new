import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./sirius.db"
    
    # Security
    secret_key: str = "dev-super-secret-key-32-characters-long-2024"
    session_max_age: int = 86400  # 24 hours
    
    # Telegram notifications
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Email (optional)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v == "dev-secret-key-change-in-production" and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY must be changed in production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    class Config:
        # env_file = ".env"  # Отключено из-за проблем с кодировкой
        case_sensitive = False


# Используем только переменные окружения и значения по умолчанию
settings = Settings()
