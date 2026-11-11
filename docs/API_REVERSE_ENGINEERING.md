# Reverse Engineering API маркетов (MRKT, Portals, Tonnel)

## ⚠️ Дисклеймер

Эта документация описывает, как найти публичные эндпоинты мини-аппов Telegram для **чтения данных о листингах**. Это может нарушать Условия использования маркетов. Используйте на свой риск, ознакомьтесь с ToS каждого маркета перед коммерческим использованием.

---

## Почему это нужно

В ТЗ указано: «Найти официальную документацию или партнёрский API, если его нет — изучить публичные запросы мини-аппа». Официальных API у этих маркетов нет, а данные листингов публично доступны через мини-аппы в Telegram.

---

## Общий алгоритм

### Шаг 1. Открыть мини-апп в браузере с DevTools

1. Открыть Telegram Web (`web.telegram.org`) или Telegram Desktop
2. Перейти к нужному маркету (например, @MRKT_Bot → кнопка «Открыть»)
3. Открыть мини-апп (обычно в iframe на домене типа `*.telegram.org` или собственном домене маркета)
4. **Важно:** использовать DevTools именно того окна, где открылся мини-апп

### Шаг 2. Включить фильтр Network

В DevTools → вкладка **Network**:
- Фильтр: `Fetch/XHR`
- Отметить **Preserve log** (чтобы не терять запросы при навигации)
- Очистить список (🚫)

### Шаг 3. Навигация по маркету

Выполнить действия, которые вызывают загрузку данных:
- Открыть главную страницу со списком подарков
- Открыть карточку подарка
- Открыть историю продаж
- Изменить фильтры (сортировка, выбор коллекции)

### Шаг 4. Анализ запросов

Для каждого XHR-запроса смотреть:
- **URL** — полный эндпоинт
- **Method** — GET/POST
- **Query/Payload** — параметры запроса
- **Response** — JSON-ответ

Искать запросы, содержащие в URL или payload характерные слова: `gifts`, `listings`, `orders`, `sales`, `resale`, `history`, `floor`.

### Шаг 5. Проверка эндпоинта

Скопировать URL + payload и проверить через curl:
```bash
curl -X POST "https://api.example.com/v1/gifts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token из запроса>" \
  -d '{"collectionId": 123, "limit": 50}'
```

### Шаг 6. Зафиксировать в конфиге

После нахождения эндпоинтов добавить в `src/collectors/` реальные адаптеры, а параметры (комиссии, лимиты) — в `config.yaml`.

---

## Что фиксировать для каждого маркета

| Параметр | Пример | Зачем |
|----------|--------|-------|
| Base URL | `https://api.example.com` | Базовый адрес |
| Эндпоинт листингов | `POST /v1/gifts` | Основные данные |
| Эндпоинт продаж | `POST /v1/gifts/{id}/sales` | История |
| Параметры пагинации | `offset`, `limit` | Постраничный обход |
| Фильтр коллекции | `collectionId` | Точечный запрос |
| Заголовки авторизации | `Authorization: Bearer ...` | Нужен для запросов |
| Комиссия | `5%` | → `config.yaml:markets.<name>.fee` |
| Лимит запросов | `30 req/min` | → backoff-логика |
| Формат ответа | JSON-схема | → маппинг в `Listing` |

---

## Маркет: MRKT

**Точки входа для проверки:**
- Официальный сайт MRKT (если есть раздел API)
- Мини-апп в Telegram
- GitHub: поиск по запросам `MRKT API` / `mrkt api endpoint`

**Что искать:**
- Список NFT-подарков с ценами
- История продаж
- Текущий floor по коллекции

**Типичные параметры:**
```
limit, offset, sortBy, collectionId, currency
```

---

## Маркет: Portals

**Точки входа:**
- Мини-апп в Telegram (@PortalsMarket или аналог)
- Сайт порталов

**Особенности:**
- Часто использует GraphQL — в DevTools смотреть вкладку **Network → Fetch/XHR**, тело запроса содержит `query` с GraphQL-операцией
- GraphQL удобно: сразу видно структуру данных

**Пример GraphQL-запроса:**
```graphql
query GetGifts($collectionId: ID!, $limit: Int!) {
  gifts(collectionId: $collectionId, limit: $limit) {
    id
    number
    price { amount currency }
    model { id name }
    backdrop { id name }
  }
}
```

---

## Маркет: Tonnel

**Точки входа:**
- Мини-апп
- Сайт tonnel.io

**Что искать:**
- Листинги по коллекциям
- История продаж (для калибровки премий красивых номеров)

---

## Ограничения и rate limits

Общие правила при работе с любым маркетом:

1. **Начинать с 1 запроса в 5 секунд.** Не более 12 req/min на старте.
2. **Наблюдать за `429 Too Many Requests`.** При получении:
   - Экспоненциальная пауза: 1с → 2с → 4с → 8с (максимум 30с)
   - Jitter: ±10% от паузы, чтобы не синхронизировать запросы
   - Автоснижение частоты опроса до 2–3 секунд между запросами
3. **Кэшировать.** Не запрашивать один и тот же лот повторно чаще, чем раз в минуту.
4. **Использовать `If-None-Match` / ETag** если сервер поддерживает — экономит трафик.

Реализация backoff уже подготовлена в `src/engine/mode2.py` (конфиг `mode2.rate_limit`).

---

## Шаблон реального адаптера

```python
import httpx
from src.collectors.base import MarketAdapter
from src.collectors.types import Listing


class RealMRKTAdapter(MarketAdapter):
    """Реальный адаптер MRKT (после reverse engineering)."""
    
    def __init__(self):
        super().__init__(name="mrkt", fee_pct=0.06, currency="TON")
        self.base_url = "https://<найденный-endpoint>"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=10.0,
            headers={"Authorization": "Bearer <токен>"}
        )
        self._delay = 1.0
    
    async def fetch_listings(
        self,
        collection: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        **kwargs
    ) -> list[Listing]:
        params = {"limit": limit, "offset": offset}
        if collection:
            params["collectionId"] = collection
        
        for attempt in range(5):
            try:
                resp = await self.client.get("/gifts", params=params)
                
                if resp.status_code == 429:
                    # Экспоненциальная пауза с jitter
                    delay = min(self._delay * (2 ** attempt), 30.0)
                    jitter = delay * 0.1 * random.uniform(-1, 1)
                    await asyncio.sleep(delay + jitter)
                    self._delay = min(self._delay * 2, 30.0)
                    continue
                
                resp.raise_for_status()
                data = resp.json()
                self._delay = 1.0  # сброс после успеха
                
                return [self._map_listing(item) for item in data["items"]]
            
            except httpx.HTTPError as e:
                logger.warning(f"Ошибка MRKT: {e}")
                await asyncio.sleep(self._delay)
                self._delay = min(self._delay * 2, 30.0)
        
        return []
    
    def _map_listing(self, item: dict) -> Listing:
        """Маппинг JSON-ответа в Listing."""
        return Listing(
            market=self.name,
            external_id=str(item["id"]),
            collection=item["collection"]["title"],
            gift_number=item["number"],
            model=item["model"]["name"],
            backdrop=item["backdrop"]["name"],
            symbol=item.get("symbol", {}).get("name"),
            price_ton=float(item["price"]["amount"]),
            price_raw=float(item["price"]["amount"]),
            currency=self.currency,
            url=item["url"],
            seen_at=datetime.utcnow()
        )
    
    async def close(self):
        await self.client.aclose()
```

---

## Чек-лист после нахождения эндпоинтов

- [ ] Эндпоинт подтверждён через curl/httpx
- [ ] Заголовки авторизации определены и добавлены в `.env` (не в код)
- [ ] Комиссия маркета зафиксирована в `config.yaml`
- [ ] Лимит запросов зафиксирован в `config.yaml`
- [ ] Реальный адаптер написан и подключён вместо mock
- [ ] Unit-тест на маппинг JSON → `Listing` написан
- [ ] Обработка `429` реализована с backoff
- [ ] Пагинация обходится полностью (offset/last_id)
- [ ] Формат ответа документирован в `docs/`
