"""Фикстуры для mock-адаптеров."""
import random
from datetime import datetime, timedelta

from .types import Listing, Sale


# Примерные коллекции
COLLECTIONS = ["Jolly Chimp", "Delicious Cake", "Green Star", "Red Ruby"]

# Примерные модели и фоны
MODELS = ["model_red", "model_blue", "model_green", "model_gold", "model_silver"]
BACKDROPS = ["backdrop_dark", "backdrop_light", "backdrop_gradient", "backdrop_solid"]
SYMBOLS = ["symbol_star", "symbol_heart", "symbol_moon", None]


def generate_mock_listings(
    market: str,
    count: int = 50,
    collection: str | None = None,
    sort_by_num: bool = False
) -> list[Listing]:
    """Генерация mock-листингов."""
    listings = []
    
    for i in range(count):
        coll = collection or random.choice(COLLECTIONS)
        
        if sort_by_num:
            # Для режима 3: низкие номера
            gift_num = i + 1
        else:
            gift_num = random.randint(1, 10000)
        
        price_ton = round(random.uniform(5, 200), 2)
        
        listing = Listing(
            market=market,
            external_id=f"{market}_{coll}_{gift_num}_{i}",
            collection=coll,
            gift_number=gift_num,
            model=random.choice(MODELS),
            backdrop=random.choice(BACKDROPS),
            symbol=random.choice(SYMBOLS),
            price_ton=price_ton,
            price_raw=price_ton,
            currency="TON",
            url=f"https://{market}.example.com/listing/{i}",
            seen_at=datetime.utcnow()
        )
        listings.append(listing)
    
    if sort_by_num:
        listings.sort(key=lambda x: x.gift_number)
    
    return listings


def generate_mock_sales(
    market: str,
    count: int = 30,
    collection: str | None = None,
    days: int = 7
) -> list[Sale]:
    """Генерация mock-продаж."""
    sales = []
    now = datetime.utcnow()
    
    for i in range(count):
        coll = collection or random.choice(COLLECTIONS)
        
        # Случайное время продажи за последние N дней
        sold_at = now - timedelta(
            seconds=random.randint(0, days * 86400)
        )
        
        # Время листинга перед продажей
        duration_sec = random.randint(3600, 72 * 3600)  # от 1ч до 3д
        listed_at = sold_at - timedelta(seconds=duration_sec)
        
        sale = Sale(
            market=market,
            collection=coll,
            model=random.choice(MODELS),
            backdrop=random.choice(BACKDROPS),
            gift_number=random.randint(1, 10000),
            price_ton=round(random.uniform(10, 150), 2),
            listed_at=listed_at,
            sold_at=sold_at,
            duration_sec=duration_sec,
            source="api"
        )
        sales.append(sale)
    
    return sales
