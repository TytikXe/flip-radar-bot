# Настройка MTProto API для внутреннего маркета Telegram

## ⚠️ Риски безопасности

**ВНИМАНИЕ:** Использование автоматизации через MTProto API может привести к:
- Бану аккаунта Telegram (ToS violation)
- Блокировке по IP
- Потере доступа к сервисному аккаунту

**Рекомендации:**
- Используйте отдельный сервисный аккаунт (не основной)
- Никогда не вызывайте методы покупки (`buyGift`, `sendGift`)
- Начинайте с низкой частоты запросов (1 запрос / 5 секунд)
- Мониторьте `FloodWait` и увеличивайте задержки при получении ошибок

## Шаг 1: Получение API_ID и API_HASH

1. Зайти на https://my.telegram.org
2. Войти под аккаунтом, который будет использоваться для бота
3. Перейти в "API development tools"
4. Создать новое приложение:
   - App title: `Flip Radar Collector` (или любое)
   - Short name: `flipradar`
   - Platform: `Other`
5. Скопировать `api_id` и `api_hash`

## Шаг 2: Настройка .env

Добавить в `.env`:
```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

## Шаг 3: Создание сессии Pyrogram

Запустить один раз для создания `.session` файла:

```bash
python scripts/create_mtproto_session.py
```

Скрипт `scripts/create_mtproto_session.py`:
```python
from pyrogram import Client
from src.config import settings

app = Client(
    "flipradar_session",
    api_id=settings.api_id,
    api_hash=settings.api_hash
)

async def main():
    async with app:
        print(f"Сессия создана: {app.name}.session")
        print("Добавьте файл в .gitignore!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Шаг 4: Реализация реального адаптера

Заменить `TelegramInternalMockAdapter` на реальный адаптер:

```python
from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.raw.types import InputUser

class TelegramInternalAdapter(MarketAdapter):
    """Реальный адаптер внутреннего маркета Telegram."""
    
    def __init__(self):
        super().__init__(
            name="telegram_internal",
            fee_pct=config.markets.get("telegram_internal", {}).get("fee", 0.15),
            currency="STARS"
        )
        
        self.client = Client(
            "flipradar_session",
            api_id=settings.api_id,
            api_hash=settings.api_hash
        )
        self.stars_to_ton = config.markets.get("telegram_internal", {}).get("stars_to_ton", 0.05)
    
    async def fetch_listings(
        self,
        collection: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs
    ) -> list[Listing]:
        """Получение листингов через MTProto."""
        sort_by_num = kwargs.get("sort_by_num", False)
        
        try:
            # Вызов MTProto API
            result = await self.client.invoke(
                functions.payments.GetResaleStarGifts(
                    # gift_id=... (если нужна конкретная коллекция)
                    sort_by_num=sort_by_num,
                    offset=str(offset),
                    limit=limit
                )
            )
            
            listings = []
            for gift in result.gifts:
                listing = Listing(
                    market="telegram_internal",
                    external_id=str(gift.id),
                    collection=gift.sticker.gift.title or "Unknown",
                    gift_number=gift.num,
                    model=gift.model_attribute_id,
                    backdrop=gift.backdrop_attribute_id,
                    symbol=gift.symbol_attribute_id,
                    price_ton=gift.price * self.stars_to_ton,
                    price_raw=gift.price,
                    currency="STARS",
                    url=f"https://t.me/gift/{gift.id}",
                    seen_at=datetime.utcnow()
                )
                listings.append(listing)
            
            return listings
        
        except FloodWait as e:
            logger.warning(f"FloodWait: {e.value} секунд, ждём...")
            await asyncio.sleep(e.value)
            return []
        
        except Exception as e:
            logger.error(f"Ошибка MTProto API: {e}")
            return []
    
    async def close(self):
        """Закрытие клиента."""
        await self.client.stop()
```

## Шаг 5: Проверка

Запустить тестовый скрипт:

```bash
python scripts/test_mtproto_collector.py
```

Скрипт `scripts/test_mtproto_collector.py`:
```python
from src.collectors.telegram_internal import TelegramInternalAdapter

async def main():
    adapter = TelegramInternalAdapter()
    
    try:
        listings = await adapter.fetch_listings(limit=10)
        print(f"Получено {len(listings)} листингов")
        
        for listing in listings[:3]:
            print(f"  #{listing.gift_number}: {listing.price_ton} TON ({listing.price_raw} STARS)")
    
    finally:
        await adapter.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Шаг 6: Мониторинг

Следить за:
- `FloodWait` ошибками в логах
- Частотой запросов (не более 1 запроса / 5 секунд на старте)
- Статусом аккаунта (не заблокирован ли)

Если получаете `FloodWait > 300 секунд` — снизить частоту запросов в 2 раза.

## Альтернатива: Telethon

Если Pyrogram не работает, можно использовать Telethon:

```python
from telethon import TelegramClient

client = TelegramClient('flipradar_session', api_id, api_hash)

async with client:
    result = await client(GetResaleStarGiftsRequest(...))
```

Синтаксис методов может отличаться, см. документацию Telethon.

---

**Важно:** Этот метод нарушает ToS Telegram. Используйте на свой риск.
