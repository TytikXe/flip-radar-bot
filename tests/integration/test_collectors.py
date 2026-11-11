"""Интеграционные тесты на MockAdapter."""
import pytest

from src.collectors.mock_adapters import create_adapters
from src.collectors.types import Listing


class TestMockAdapters:
    """Тесты mock-адаптеров."""
    
    def test_create_all_adapters(self):
        """Создаются все 4 адаптера."""
        adapters = create_adapters()
        
        assert len(adapters) == 4
        assert "telegram" in adapters
        assert "mrkt" in adapters
        assert "portals" in adapters
        assert "tonnel" in adapters
    
    def test_adapter_names_and_fees(self):
        """У каждого адаптера свой name и fee."""
        adapters = create_adapters()
        
        assert adapters["telegram"].name == "telegram"
        assert adapters["mrkt"].name == "mrkt"
        assert adapters["portals"].name == "portals"
        assert adapters["tonnel"].name == "tonnel"
        
        # Комиссии в разумных пределах
        for adapter in adapters.values():
            assert 0 < adapter.fee_pct < 0.5
    
    @pytest.mark.asyncio
    async def test_fetch_listings(self):
        """Адаптер возвращает листинги."""
        adapters = create_adapters()
        
        for name, adapter in adapters.items():
            listings = await adapter.fetch_listings(limit=10)
            
            assert len(listings) == 10, f"{name} вернул {len(listings)} вместо 10"
            assert all(isinstance(l, Listing) for l in listings)
    
    @pytest.mark.asyncio
    async def test_fetch_listings_with_collection(self):
        """Фильтрация по коллекции работает."""
        adapters = create_adapters()
        
        listings = await adapters["mrkt"].fetch_listings(
            collection="Jolly Chimp",
            limit=20
        )
        
        assert len(listings) == 20
        assert all(l.collection == "Jolly Chimp" for l in listings)
    
    @pytest.mark.asyncio
    async def test_fetch_listings_pagination(self):
        """Пагинация через offset работает."""
        adapter = create_adapters()["mrkt"]
        
        page1 = await adapter.fetch_listings(limit=5, offset=0)
        page2 = await adapter.fetch_listings(limit=5, offset=5)
        
        assert len(page1) == 5
        assert len(page2) == 5
        
        # Лоты не должны пересекаться
        ids1 = {l.external_id for l in page1}
        ids2 = {l.external_id for l in page2}
        assert ids1.isdisjoint(ids2)
    
    @pytest.mark.asyncio
    async def test_fetch_sales(self):
        """Адаптер возвращает продажи."""
        from src.collectors.types import Sale
        
        adapters = create_adapters()
        
        for name, adapter in adapters.items():
            sales = await adapter.fetch_sales(days=7, limit=15)
            
            assert len(sales) == 15, f"{name} вернул {len(sales)} вместо 15"
            assert all(isinstance(s, Sale) for s in sales)
            assert all(s.duration_sec > 0 for s in sales)
    
    @pytest.mark.asyncio
    async def test_telegram_stars_conversion(self):
        """Telegram: цена конвертируется Stars → TON."""
        adapter = create_adapters()["telegram"]
        
        listings = await adapter.fetch_listings(limit=5)
        
        for listing in listings:
            assert listing.currency == "STARS"
            assert listing.price_raw > 0  # в Stars
            assert listing.price_ton > 0  # в TON
    
    @pytest.mark.asyncio
    async def test_sort_by_num(self):
        """Параметр sort_by_num передаётся в адаптер."""
        adapter = create_adapters()["telegram"]
        
        listings = await adapter.fetch_listings(
            limit=10,
            sort_by_num=True
        )
        
        assert len(listings) == 10
        # Номера должны быть отсортированы по возрастанию
        numbers = [l.gift_number for l in listings]
        assert numbers == sorted(numbers)
