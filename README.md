# Flip Radar — Telegram-бот для флиппинга NFT-подарков

**Статус:** MVP с mock-адаптерами (требуется интеграция с реальными API)

## 🎯 Возможности

Три режима поиска выгодных сделок:

1. **Flip Radar** — арбитраж между маркетами (Telegram, MRKT, Portals, Tonnel)
2. **Mono Sniper** — монохромные подарки по цене ≤ floor
3. **Красивые номера** — редкие порядковые номера (#1, #777, палиндромы, лесенки)

**Тарифы:**
- Free: 3 алерта/день (режим 1), задержка 5 мин (режимы 2, 3)
- Pro: без ограничений, мгновенные алерты

## 🚀 Быстрый старт

### 1. Требования

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

### 2. Настройка

```bash
# Клонировать репозиторий
git clone <repo_url>
cd flip-radar

# Создать .env файл
cp .env.example .env

# Заполнить BOT_TOKEN от @BotFather
nano .env
```

Обязательные переменные:
```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql+asyncpg://flipradar:password@db:5432/flipradar
REDIS_URL=redis://redis:6379/0
```

### 3. Запуск через Docker

```bash
# Сборка и запуск
docker compose up --build

# Проверка логов
docker logs -f flipradar_bot

# Остановка
docker compose down
```

### 4. Локальный запуск (без Docker)

```bash
# Установка зависимостей
poetry install

# Запуск PostgreSQL и Redis локально
# ...

# Применение миграций
alembic upgrade head

# Запуск бота
python src/bot/main.py
```

## 📋 Команды бота

- `/start` — начало работы, выбор профиля
- `/modes` — включение/выключение режимов
- `/deals` — топ-10 актуальных сделок
- `/mydeals` — учёт своих сделок
- `/pro` — оформить Pro подписку
- `/help` — справка

## 🔧 Архитектура

```
src/
├── collectors/       # Адаптеры маркетов (mock и заглушки для реальных)
├── engine/          # Вычисления: fair price, net profit, scoring, beauty_tier
├── notifier/        # Форматирование и отправка алертов
├── bot/             # aiogram 3, хендлеры, клавиатуры
├── database/        # SQLAlchemy модели, миграции
└── config.py        # Загрузка config.yaml и .env
```

## ⚠️ Ограничения MVP

### Требуется доработка:

1. **Внутренний маркет Telegram (MTProto)**
   - Нужен `API_ID` и `API_HASH` от https://my.telegram.org
   - Риск бана аккаунта за автоматизацию
   - См. `docs/MTPROTO_SETUP.md`

2. **API маркетов (MRKT, Portals, Tonnel)**
   - Публичные API не документированы
   - Требуется reverse-engineering мини-аппов
   - См. `docs/API_REVERSE_ENGINEERING.md`

3. **Цветовой анализ (режим 2)**
   - Реальный `mono_score` требует image processing
   - В MVP используется предрасчитанная таблица
   - См. TODO в `src/engine/mode2.py`

4. **Реальные комиссии и курсы**
   - Значения в `config.yaml` примерные
   - Проверить актуальные на маркетах

### Готово к использованию:

✅ Полная схема БД (PostgreSQL + Alembic)  
✅ Mock-адаптеры для всех 4 маркетов  
✅ Логика всех 3 режимов  
✅ Бот (команды, кнопки, FSM)  
✅ Unit-тесты (beauty_tier, расчёты)  
✅ Docker Compose  

## 🧪 Тесты

```bash
# Запуск всех тестов
pytest

# С покрытием
pytest --cov=src tests/

# Только unit-тесты
pytest tests/unit/
```

## 📚 Документация

- [CONSTRAINTS_AND_ASSUMPTIONS.md](CONSTRAINTS_AND_ASSUMPTIONS.md) — ограничения MVP
- [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md) — 95 критериев приёмки
- [docs/MTPROTO_SETUP.md](docs/MTPROTO_SETUP.md) — настройка MTProto API
- [docs/API_REVERSE_ENGINEERING.md](docs/API_REVERSE_ENGINEERING.md) — поиск эндпоинтов маркетов

## 🔐 Безопасность

⚠️ **Важно:**
- Бот НЕ покупает подарки сам
- НЕ хранит сид-фразы и ключи
- НЕ требует бизнес-доступ к аккаунту
- Кнопка «Купить» — это ссылка на маркет

Все секреты только в `.env` (не коммитить!).

## 📝 Лицензия

MIT

---

**Разработка:** Flip Radar Team  
**Дата:** 2026-11-12
