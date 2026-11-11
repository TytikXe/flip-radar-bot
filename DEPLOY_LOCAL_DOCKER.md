# 🏠 ЗАПУСК БОТА ЛОКАЛЬНО (НА ТВОЁМ КОМПЬЮТЕРЕ)

## ✅ САМЫЙ БЫСТРЫЙ СПОСОБ — БЕЗ РЕГИСТРАЦИЙ

**Бот будет работать, пока компьютер включён.**

---

## Шаг 1: Установить Docker Desktop

1. Скачай Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Запусти установщик
3. Дождись окончания установки
4. Перезагрузи компьютер (если попросит)
5. Запусти **Docker Desktop** (ярлык на рабочем столе)
6. Дождись, пока Docker запустится (иконка кита в трее должна стать зелёной)

---

## Шаг 2: Проверить установку Docker

Открой PowerShell и выполни:

```powershell
docker --version
docker-compose --version
```

Должны увидеть версии (например, `Docker version 24.0.7`).

---

## Шаг 3: Перейти в папку проекта

```powershell
cd "C:\MainMalbara\Бот для флиппинга"
```

---

## Шаг 4: Проверить `.env` файл

Убедись, что файл `.env` содержит токен бота:

```powershell
cat .env
```

Должен увидеть:
```env
BOT_TOKEN=9054803178:AAEzqn1M4d2iZFDM6yfqEBAmeEN8Bqfgu5E
DATABASE_URL=postgresql+asyncpg://flipradar:password@db:5432/flipradar
REDIS_URL=redis://redis:6379/0
...
```

Если `BOT_TOKEN` пустой или закомментирован — **исправь вручную** в блокноте.

---

## Шаг 5: Запустить бота

```powershell
docker-compose up --build
```

**Что произойдёт:**
1. Docker соберёт образ бота (3–5 минут в первый раз)
2. Запустит 3 контейнера:
   - `flipradar_db` (PostgreSQL)
   - `flipradar_redis` (Redis)
   - `flipradar_bot` (твой бот)
3. Применит миграции Alembic
4. Запустит бота

**Ждать, пока увидишь:**
```
flipradar_bot | INFO: Бот запущен
flipradar_bot | INFO: Polling started
```

---

## Шаг 6: Проверить в Telegram

1. Открой Telegram
2. Найди бота (через @BotFather или поиск по токену)
3. Отправь `/start`
4. Должен ответить с выбором профиля

---

## Шаг 7: Остановить бота

**Не закрывай окно PowerShell!** Нажми **Ctrl+C** → бот остановится.

Или в новом окне PowerShell:

```powershell
cd "C:\MainMalbara\Бот для флиппинга"
docker-compose down
```

---

## Шаг 8: Запустить снова

```powershell
cd "C:\MainMalbara\Бот для флиппинга"
docker-compose up
```

(Без `--build`, потому что образ уже собран)

---

## Запуск в фоне (чтобы закрыть окно)

Если хочешь, чтобы бот работал фоном:

```powershell
docker-compose up -d
```

Проверить статус:
```powershell
docker-compose ps
```

Посмотреть логи:
```powershell
docker-compose logs -f bot
```

Остановить:
```powershell
docker-compose down
```

---

## 🎉 ГОТОВО!

Бот работает на твоём компьютере.

---

## Плюсы и минусы локального запуска

### ✅ Плюсы:
- Бесплатно навсегда
- Не нужны регистрации
- Полный контроль
- Быстро запускается

### ❌ Минусы:
- Работает только пока компьютер включён
- Нет автоматических обновлений
- Нужно вручную перезапускать после изменений

---

## Если хочешь, чтобы бот работал 24/7:

Используй **Railway** (бесплатно 500 часов/месяц):
- [DEPLOY_RAILWAY_CLI.md](DEPLOY_RAILWAY_CLI.md) — через команды
- [DEPLOY_RAILWAY_WEB.md](DEPLOY_RAILWAY_WEB.md) — через сайт

---

## Проблемы и решения

### Ошибка: "Docker daemon is not running"
**Решение:** Запусти Docker Desktop и подожди, пока иконка кита станет зелёной.

### Ошибка: "port is already allocated"
**Решение:** Другое приложение занимает порт. Останови его или измени порты в `docker-compose.yml`.

### Ошибка: "BOT_TOKEN not set"
**Решение:** Проверь файл `.env` — токен должен быть без кавычек и без пробелов.

### Ошибка: "Cannot connect to database"
**Решение:** Подожди 10–15 секунд — PostgreSQL медленно запускается в первый раз.

---

**Нужна помощь?** Пришли скриншот ошибки сюда!
