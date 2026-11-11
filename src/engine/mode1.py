"""Вычисления для режима 1: Flip Radar."""
from datetime import datetime, timedelta
from typing import Optional

from src.config import config
from src.database.models import Sale


class FairPrice:
    """Расчёт справедливой цены."""
    
    @staticmethod
    def calculate(
        sales: list[Sale],
        floor_model: Optional[float] = None,
        floor_collection: Optional[float] = None
    ) -> tuple[float, str]:
        """
        Расчёт fair price и уровня доверия.
        
        Args:
            sales: Список продаж за последние 7 дней (model + backdrop)
            floor_model: Floor модели
            floor_collection: Floor коллекции
        
        Returns:
            (fair_price, confidence)
        """
        mode1_cfg = config.mode1
        min_sales = mode1_cfg["fair_price"]["min_sales_count"]
        thresholds = mode1_cfg["fair_price"]["confidence_thresholds"]
        
        if len(sales) >= thresholds["high"]:
            # Достаточно данных: медиана последних 10 продаж
            prices = sorted([s.price_ton for s in sales[-min_sales:]])
            median_idx = len(prices) // 2
            fair_price = prices[median_idx]
            confidence = "high"
        
        elif len(sales) >= thresholds["mid"]:
            # Средне: медиана имеющихся продаж
            prices = sorted([s.price_ton for s in sales])
            median_idx = len(prices) // 2
            fair_price = prices[median_idx]
            confidence = "mid"
        
        elif floor_model is not None:
            # Мало продаж: floor модели
            fair_price = floor_model
            confidence = "low"
        
        elif floor_collection is not None:
            # Совсем нет данных: floor коллекции
            fair_price = floor_collection
            confidence = "low"
        
        else:
            # Нет никаких данных
            raise ValueError("Недостаточно данных для расчёта fair price")
        
        return fair_price, confidence


class NetProfit:
    """Расчёт чистой прибыли."""
    
    @staticmethod
    def calculate(
        buy_price: float,
        buy_market_fee: float,
        sell_price: float,
        sell_market_fee: float,
        transfer_cost: float = 0.0
    ) -> float:
        """
        Расчёт чистой прибыли после комиссий.
        
        Formula: net = sell_price × (1 - fee_sell) - buy_price - transfer_cost
        
        Args:
            buy_price: Цена покупки
            buy_market_fee: Комиссия маркета покупки (0.05 = 5%)
            sell_price: Цена продажи
            sell_market_fee: Комиссия маркета продажи
            transfer_cost: Стоимость перевода между маркетами
        
        Returns:
            Чистая прибыль в TON
        """
        sell_after_fee = sell_price * (1 - sell_market_fee)
        net = sell_after_fee - buy_price - transfer_cost
        return net
    
    @staticmethod
    def calculate_profit_pct(net: float, buy_price: float) -> float:
        """Процент прибыли относительно вложений."""
        if buy_price <= 0:
            return 0.0
        return (net / buy_price) * 100


class TimeToSell:
    """Расчёт времени продажи."""
    
    @staticmethod
    def calculate(sales: list[Sale]) -> dict:
        """
        Расчёт медианы и перцентилей времени продажи.
        
        Args:
            sales: Продажи за последние 7 дней (model + backdrop)
        
        Returns:
            {
                "median_hours": float,
                "p25_hours": float,
                "p75_hours": float,
                "count": int,
                "has_enough_data": bool
            }
        """
        if len(sales) < 5:
            return {
                "median_hours": None,
                "p25_hours": None,
                "p75_hours": None,
                "count": len(sales),
                "has_enough_data": False
            }
        
        durations = sorted([s.duration_sec for s in sales])
        n = len(durations)
        
        # Перцентили
        p25_idx = n // 4
        median_idx = n // 2
        p75_idx = (3 * n) // 4
        
        return {
            "median_hours": durations[median_idx] / 3600,
            "p25_hours": durations[p25_idx] / 3600,
            "p75_hours": durations[p75_idx] / 3600,
            "count": n,
            "has_enough_data": True
        }


class Scoring:
    """Скоринг лотов для режима 1."""
    
    @staticmethod
    def calculate(
        profit_pct: float,
        time_to_sell: dict,
        confidence: str,
        liquidity_score: float = 50.0
    ) -> int:
        """
        Расчёт score (0-100).
        
        Formula: score = 0.40×profit% + 0.30×speed + 0.20×confidence + 0.10×liquidity
        
        Args:
            profit_pct: Процент прибыли
            time_to_sell: Результат TimeToSell.calculate()
            confidence: 'high' / 'mid' / 'low'
            liquidity_score: Оценка ликвидности (0-100)
        
        Returns:
            Оценка от 0 до 100
        """
        weights = config.mode1["scoring_weights"]
        slow_threshold = config.mode1["slow_sale_penalty"]["threshold_hours"]
        
        # Profit: нормализуем к 0-100 (20% profit = 100 баллов)
        profit_score = min(profit_pct * 5, 100)
        
        # Speed: чем быстрее, тем лучше
        if not time_to_sell["has_enough_data"]:
            speed_score = 50.0  # Средний балл за неизвестность
        else:
            median_h = time_to_sell["median_hours"]
            if median_h > slow_threshold:
                speed_score = config.mode1["slow_sale_penalty"]["speed_score"]
            else:
                # Линейная шкала: 1ч=100, 72ч=0
                speed_score = max(0, 100 - (median_h / slow_threshold) * 100)
        
        # Confidence: high=100, mid=60, low=30
        conf_scores = {"high": 100, "mid": 60, "low": 30}
        confidence_score = conf_scores.get(confidence, 30)
        
        # Итоговый score
        score = (
            weights["profit"] * profit_score +
            weights["speed"] * speed_score +
            weights["confidence"] * confidence_score +
            weights["liquidity"] * liquidity_score
        )
        
        return int(round(score))


class ArbitrageEngine:
    """Главный движок режима 1."""
    
    def __init__(self, markets: dict):
        """
        Args:
            markets: {name: MarketAdapter}
        """
        self.markets = markets
    
    def find_best_sell_market(
        self,
        fair_price: float,
        buy_price: float,
        buy_market: str
    ) -> tuple[str, float]:
        """
        Поиск лучшего маркета для продажи.
        
        Returns:
            (market_name, net_profit)
        """
        best_market = None
        best_net = float("-inf")
        
        buy_adapter = self.markets[buy_market]
        
        for sell_name, sell_adapter in self.markets.items():
            # Transfer cost только если маркеты разные
            transfer = 0.0
            if sell_name != buy_market and sell_adapter.currency == "TON":
                transfer = config.markets[sell_name].get("transfer_cost_ton", 0.5)
            
            net = NetProfit.calculate(
                buy_price=buy_price,
                buy_market_fee=buy_adapter.fee_pct,
                sell_price=fair_price,
                sell_market_fee=sell_adapter.fee_pct,
                transfer_cost=transfer
            )
            
            if net > best_net:
                best_net = net
                best_market = sell_name
        
        return best_market, best_net
