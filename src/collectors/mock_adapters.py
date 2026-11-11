"""Mock-адаптеры для всех маркетов."""
import asyncio
from typing import Optional

from src.config import config
from .base import MarketAdapter
from .fixtures import generate_mock_listings, generate_mock_sales
from .types import Listing, Sale


class MockAdapter(MarketAdapter):
    """Базовый mock-адаптер."""
    
    async def fetch_listings(
        self,
        collection: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs
    ) -> list[Listing]:
        """Генерация mock-листингов."""
        # Имитация задержки сети
        await asyncio.sleep(0.1)
        
        sort_by_num = kwargs.get("sort_by_num", False)
        # Генерируем больше элементов для поддержки offset
        total_count = offset + limit
        listings = generate_mock_listings(
            self.name,
            count=total_count,
            collection=collection,
            sort_by_num=sort_by_num
        )
        
        return listings[offset:offset + limit]
    
    async def fetch_sales(
        self,
        collection: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> list[Sale]:
        """Генерация mock-продаж."""
        await asyncio.sleep(0.1)
        
        sales = generate_mock_sales(
            self.name,
            count=limit,
            collection=collection,
            days=days
        )
        
        return sales


class MockTelegramMarketAdapter(MockAdapter):
    """Mock-адаптер внутреннего маркета Telegram."""
    
    def __init__(self):
        market_cfg = config.markets.get("telegram", {})
        super().__init__(
            name="telegram",
            fee_pct=market_cfg.get("fee", 0.05),
            currency="STARS"
        )
        self.stars_to_ton = market_cfg.get("stars_to_ton", 0.05)
    
    async def fetch_listings(
        self,
        collection: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs
    ) -> list[Listing]:
        """Листинги с конвертацией Stars → TON."""
        listings = await super().fetch_listings(collection, limit, offset, **kwargs)
        
        # Конвертация цены
        for listing in listings:
            listing.price_raw = listing.price_ton * 20  # 1 TON = ~20 STARS
            listing.price_ton = listing.price_raw * self.stars_to_ton
            listing.currency = "STARS"
        
        return listings


class MockMRKTAdapter(MockAdapter):
    """Mock-адаптер MRKT."""
    
    def __init__(self):
        market_cfg = config.markets.get("mrkt", {})
        super().__init__(
            name="mrkt",
            fee_pct=market_cfg.get("fee", 0.06),
            currency="TON"
        )


class MockPortalsAdapter(MockAdapter):
    """Mock-адаптер Portals."""
    
    def __init__(self):
        market_cfg = config.markets.get("portals", {})
        super().__init__(
            name="portals",
            fee_pct=market_cfg.get("fee", 0.035),
            currency="TON"
        )


class MockTonnelAdapter(MockAdapter):
    """Mock-адаптер Tonnel."""
    
    def __init__(self):
        market_cfg = config.markets.get("tonnel", {})
        super().__init__(
            name="tonnel",
            fee_pct=market_cfg.get("fee", 0.05),
            currency="TON"
        )


# Фабрика адаптеров
def create_adapters() -> dict[str, MarketAdapter]:
    """Создание всех адаптеров."""
    return {
        "telegram": MockTelegramMarketAdapter(),
        "mrkt": MockMRKTAdapter(),
        "portals": MockPortalsAdapter(),
        "tonnel": MockTonnelAdapter(),
    }
