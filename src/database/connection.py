"""Подключение к базе данных."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
)

from src.config import settings


class Database:
    """Управление подключением к PostgreSQL."""
    
    def __init__(self, url: str):
        """Инициализация engine и session factory."""
        self.engine: AsyncEngine = create_async_engine(
            url,
            echo=settings.log_level == "DEBUG",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер для сессии."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def close(self):
        """Закрытие engine."""
        await self.engine.dispose()


# Глобальный экземпляр (lazy initialization)
_db: Database | None = None


def get_db() -> Database:
    """Получить экземпляр БД (ленивая инициализация)."""
    global _db
    if _db is None:
        _db = Database(settings.database_url)
    return _db


# Для обратной совместимости
db = None  # Будет инициализирован при первом обращении
