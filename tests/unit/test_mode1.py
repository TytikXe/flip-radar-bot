"""Unit-тесты для режима 1: Flip Radar."""
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

from src.engine.mode1 import (
    FairPrice, NetProfit, TimeToSell, Scoring
)


@dataclass
class MockSale:
    """Mock модели Sale для тестов."""
    market: str
    collection: str
    model: str
    backdrop: str
    gift_number: int
    price_ton: float
    listed_at: datetime
    sold_at: datetime
    duration_sec: int
    source: str


class TestFairPrice:
    """Тесты расчёта справедливой цены."""
    
    def test_high_confidence(self):
        """≥10 продаж → медиана, high confidence."""
        sales = [
            MockSale(
                market="mrkt",
                collection="Test",
                model="m1",
                backdrop="b1",
                gift_number=i,
                price_ton=10 + i,
                listed_at=datetime.utcnow(),
                sold_at=datetime.utcnow(),
                duration_sec=3600,
                source="api"
            )
            for i in range(12)
        ]
        
        fair, conf = FairPrice.calculate(sales)
        
        # Медиана последних 10 продаж: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        # Берём отсортированный список price_ton
        # sales = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        # последние 10: sales[-10:] = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        # отсортированные prices = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        # median_idx = 10 // 2 = 5
        # fair_price = prices[5] = 17
        assert fair == 17.0
        assert conf == "high"
    
    def test_mid_confidence(self):
        """3-9 продаж → медиана, mid confidence."""
        sales = [
            MockSale(
                market="mrkt",
                collection="Test",
                model="m1",
                backdrop="b1",
                gift_number=i,
                price_ton=20 + i * 2,
                listed_at=datetime.utcnow(),
                sold_at=datetime.utcnow(),
                duration_sec=3600,
                source="api"
            )
            for i in range(5)
        ]
        
        fair, conf = FairPrice.calculate(sales)
        
        # Медиана [20, 22, 24, 26, 28] = 24
        assert fair == 24.0
        assert conf == "mid"
    
    def test_low_confidence_floor_model(self):
        """<3 продаж → floor модели, low confidence."""
        sales = [
            MockSale(
                market="mrkt",
                collection="Test",
                model="m1",
                backdrop="b1",
                gift_number=1,
                price_ton=50.0,
                listed_at=datetime.utcnow(),
                sold_at=datetime.utcnow(),
                duration_sec=3600,
                source="api"
            )
        ]
        
        fair, conf = FairPrice.calculate(sales, floor_model=30.0)
        
        assert fair == 30.0
        assert conf == "low"
    
    def test_low_confidence_floor_collection(self):
        """Нет продаж, нет floor модели → floor коллекции."""
        fair, conf = FairPrice.calculate([], floor_collection=25.0)
        
        assert fair == 25.0
        assert conf == "low"
    
    def test_no_data(self):
        """Нет никаких данных → ошибка."""
        with pytest.raises(ValueError, match="Недостаточно данных"):
            FairPrice.calculate([])


class TestNetProfit:
    """Тесты расчёта чистой прибыли."""
    
    def test_basic_profit(self):
        """Базовый расчёт: buy 38, sell 50, fee 5%, transfer 0.5."""
        net = NetProfit.calculate(
            buy_price=38.0,
            buy_market_fee=0.05,
            sell_price=50.0,
            sell_market_fee=0.05,
            transfer_cost=0.5
        )
        
        # sell_after_fee = 50 * 0.95 = 47.5
        # net = 47.5 - 38 - 0.5 = 9.0
        assert net == pytest.approx(9.0)
    
    def test_profit_percentage(self):
        """Процент прибыли."""
        pct = NetProfit.calculate_profit_pct(net=9.0, buy_price=38.0)
        
        # (9 / 38) * 100 ≈ 23.68%
        assert pct == pytest.approx(23.68, abs=0.01)
    
    def test_zero_buy_price(self):
        """buy_price = 0 → 0% прибыли."""
        pct = NetProfit.calculate_profit_pct(10.0, 0.0)
        assert pct == 0.0


class TestTimeToSell:
    """Тесты расчёта времени продажи."""
    
    def test_enough_data(self):
        """≥5 продаж → медиана и перцентили."""
        sales = [
            MockSale(
                market="mrkt",
                collection="Test",
                model="m1",
                backdrop="b1",
                gift_number=i,
                price_ton=50.0,
                listed_at=datetime.utcnow(),
                sold_at=datetime.utcnow(),
                duration_sec=3600 * (i + 1),  # 1ч, 2ч, 3ч, 4ч, 5ч
                source="api"
            )
            for i in range(5)
        ]
        
        result = TimeToSell.calculate(sales)
        
        assert result["has_enough_data"] is True
        # durations = [3600, 7200, 10800, 14400, 18000] (1ч, 2ч, 3ч, 4ч, 5ч)
        # median_idx = 5 // 2 = 2
        # median = durations[2] = 10800 / 3600 = 3.0 часа
        assert result["median_hours"] == 3.0
        # p25_idx = 5 // 4 = 1 → durations[1] = 7200 / 3600 = 2.0
        assert result["p25_hours"] == 2.0
        # p75_idx = (3 * 5) // 4 = 3 → durations[3] = 14400 / 3600 = 4.0
        assert result["p75_hours"] == 4.0
        assert result["count"] == 5
    
    def test_not_enough_data(self):
        """<5 продаж → мало данных."""
        sales = [
            MockSale(
                market="mrkt",
                collection="Test",
                model="m1",
                backdrop="b1",
                gift_number=1,
                price_ton=50.0,
                listed_at=datetime.utcnow(),
                sold_at=datetime.utcnow(),
                duration_sec=7200,
                source="api"
            )
            for _ in range(3)
        ]
        
        result = TimeToSell.calculate(sales)
        
        assert result["has_enough_data"] is False
        assert result["median_hours"] is None
        assert result["count"] == 3


class TestScoring:
    """Тесты скоринга."""
    
    def test_high_score(self):
        """Высокий скор: profit=20%, speed=быстро, conf=high."""
        time_data = {
            "median_hours": 5.0,
            "p25_hours": 3.0,
            "p75_hours": 10.0,
            "count": 15,
            "has_enough_data": True
        }
        
        score = Scoring.calculate(
            profit_pct=20.0,
            time_to_sell=time_data,
            confidence="high",
            liquidity_score=70.0
        )
        
        # profit_score = min(20 * 5, 100) = 100
        # speed_score = 100 - (5 / 72) * 100 ≈ 93
        # confidence_score = 100
        # liquidity_score = 70
        # score = 0.4*100 + 0.3*93 + 0.2*100 + 0.1*70 ≈ 94.9
        assert 90 <= score <= 100
    
    def test_slow_sale_penalty(self):
        """Штраф за долгую продажу (>72ч)."""
        time_data = {
            "median_hours": 80.0,  # Больше 72ч
            "p25_hours": 50.0,
            "p75_hours": 100.0,
            "count": 10,
            "has_enough_data": True
        }
        
        score = Scoring.calculate(
            profit_pct=15.0,
            time_to_sell=time_data,
            confidence="mid",
            liquidity_score=50.0
        )
        
        # speed_score = 0 (штраф)
        # profit_score = 75
        # confidence_score = 60
        # liquidity_score = 50
        # score = 0.4*75 + 0.3*0 + 0.2*60 + 0.1*50 = 47
        assert 45 <= score <= 50
    
    def test_unknown_speed(self):
        """Неизвестная скорость продажи → средний балл."""
        time_data = {
            "has_enough_data": False,
            "median_hours": None,
            "count": 2
        }
        
        score = Scoring.calculate(
            profit_pct=10.0,
            time_to_sell=time_data,
            confidence="low"
        )
        
        # speed_score = 50 (средний за неизвестность)
        # profit_score = 50
        # confidence_score = 30
        # liquidity_score = 50 (default)
        # score = 0.4*50 + 0.3*50 + 0.2*30 + 0.1*50 = 46
        assert 44 <= score <= 48
