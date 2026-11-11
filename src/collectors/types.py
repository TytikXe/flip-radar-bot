"""Общие типы данных для collectors."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Listing:
    """Унифицированная модель листинга."""
    
    market: str
    external_id: str
    collection: str
    gift_number: int
    model: str
    backdrop: str
    symbol: Optional[str]
    price_ton: float
    price_raw: float
    currency: str
    url: str
    seen_at: datetime
    
    def __post_init__(self):
        """Валидация после создания."""
        if self.price_ton <= 0:
            raise ValueError(f"price_ton должна быть > 0, получено {self.price_ton}")
        if not self.url:
            raise ValueError("url не может быть пустым")


@dataclass
class Sale:
    """Унифицированная модель продажи."""
    
    market: str
    collection: str
    model: str
    backdrop: str
    gift_number: int
    price_ton: float
    listed_at: datetime
    sold_at: datetime
    duration_sec: int
    source: str  # 'api' или 'inferred'
