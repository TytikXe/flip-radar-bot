"""Интерфейс маркет-адаптера."""
from abc import ABC, abstractmethod
from typing import Optional

from .types import Listing, Sale


class MarketAdapter(ABC):
    """Базовый интерфейс для всех адаптеров маркетов."""
    
    def __init__(self, name: str, fee_pct: float, currency: str):
        """
        Args:
            name: Название маркета
            fee_pct: Комиссия (0.05 = 5%)
            currency: Валюта ('TON', 'STARS')
        """
        self.name = name
        self.fee_pct = fee_pct
        self.currency = currency
    
    @abstractmethod
    async def fetch_listings(
        self,
        collection: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs
    ) -> list[Listing]:
        """
        Получение активных листингов.
        
        Args:
            collection: Фильтр по коллекции (если None, все коллекции)
            limit: Максимум записей
            offset: Смещение
            **kwargs: Дополнительные параметры (sort_by_num, attributes и т.п.)
        
        Returns:
            Список листингов
        """
        pass
    
    @abstractmethod
    async def fetch_sales(
        self,
        collection: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> list[Sale]:
        """
        Получение истории продаж (если API поддерживает).
        
        Args:
            collection: Фильтр по коллекции
            days: За сколько дней
            limit: Максимум записей
        
        Returns:
            Список продаж (пустой список, если API не даёт историю)
        """
        pass
    
    async def close(self):
        """Закрытие соединений (если нужно)."""
        pass
