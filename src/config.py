"""Конфигурация приложения через pydantic-settings."""
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class Settings(BaseSettings):
    """Настройки из .env файла."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram Bot
    bot_token: str = Field(..., description="Токен бота от @BotFather")
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://flipradar:password@localhost:5432/flipradar"
    )
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # MTProto API (для внутреннего маркета)
    api_id: Optional[int] = Field(default=None)
    api_hash: Optional[str] = Field(default=None)
    session_string: Optional[str] = Field(default=None)
    
    # Environment
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    
    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Проверка токена бота."""
        if not v or v == "your_bot_token_here":
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        return v


class Config:
    """Конфигурация из config.yaml."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Загрузка конфигурации из YAML."""
        self.config_path = Path(config_path)
        self._data = self._load_yaml()
    
    def _load_yaml(self) -> dict:
        """Чтение YAML файла."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Конфиг не найден: {self.config_path}")
        
        with open(self.config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def get(self, path: str, default=None):
        """Получение значения по пути (напр. 'markets.mrkt.fee')."""
        keys = path.split(".")
        value = self._data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    @property
    def markets(self) -> dict:
        """Настройки всех маркетов."""
        return self._data.get("markets", {})
    
    @property
    def mode1(self) -> dict:
        """Настройки режима Flip Radar."""
        return self._data.get("mode1", {})
    
    @property
    def mode2(self) -> dict:
        """Настройки режима Mono Sniper."""
        return self._data.get("mode2", {})
    
    @property
    def mode3(self) -> dict:
        """Настройки режима Красивые номера."""
        return self._data.get("mode3", {})
    
    @property
    def tiers(self) -> dict:
        """Настройки тарифов Free/Pro."""
        return self._data.get("tiers", {})


# Глобальные экземпляры
settings = Settings()
config = Config()
