# 🚀 ДЕПЛОЙ НА RAILWAY БЕЗ GITHUB (ЧЕРЕЗ CLI)

## Шаг 1: Установить Railway CLI

Открой PowerShell от имени администратора и выполни:

```powershell
npm install -g @railway/cli
```

**Если npm не установлен:**

Скачай и установи Node.js: https://nodejs.org/en/download/
После установки перезапусти PowerShell и повтори команду выше.

---

## Шаг 2: Зарегистрироваться и войти в Railway

```powershell
railway login
```

Откроется браузер → нажми "Login with GitHub" (или Email).

---

## Шаг 3: Перейти в папку проекта

```powershell
cd "C:\MainMalbara\Бот для флиппинга"
```

---

## Шаг 4: Инициализировать Railway проект

```powershell
railway init
```

Выбери:
- **Create a new project**: Да
- **Project name**: `flip-radar-bot` (или любое)
- **Environment**: `production`

---

## Шаг 5: Добавить сервисы (PostgreSQL и Redis)

```powershell
# Добавить PostgreSQL
railway add

# В меню выбери: PostgreSQL

# Добавить Redis
railway add

# В меню выбери: Redis
```

---

## Шаг 6: Установить переменные окружения

```powershell
railway variables set BOT_TOKEN=9054803178:AAEzqn1M4d2iZFDM6yfqEBAmeEN8Bqfgu5E
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO
```

Railway автоматически добавит `DATABASE_URL` и `REDIS_URL` от созданных сервисов.

---

## Шаг 7: Задеплоить бота

```powershell
railway up
```

Подожди 2–3 минуты, пока Railway:
1. Загрузит код
2. Соберёт Docker-образ
3. Запустит контейнер
4. Применит миграции

---

## Шаг 8: Проверить логи

```powershell
railway logs
```

Должен увидеть:
```
INFO: Бот запущен
INFO: Polling started
```

---

## Шаг 9: Проверить в Telegram

1. Открой Telegram
2. Найди бота (через @BotFather или поиск по юзернейму)
3. Отправь `/start`
4. Должен ответить с выбором профиля

---

## 🎉 ГОТОВО!

Бот работает 24/7 на Railway.

---

## Управление после деплоя

### Посмотреть статус:
```powershell
railway status
```

### Открыть дашборд Railway:
```powershell
railway open
```

### Остановить бота:
```powershell
railway down
```

### Перезапустить после изменений:
```powershell
railway up
```

### Посмотреть переменные:
```powershell
railway variables
```

---

## Если что-то не работает

1. **Проверь логи:**
   ```powershell
   railway logs --tail 100
   ```

2. **Проверь статус сервисов:**
   ```powershell
   railway status
   ```

3. **Проверь переменные:**
   ```powershell
   railway variables
   ```

4. **Если ошибка "DATABASE_URL not set":**
   ```powershell
   railway link
   railway variables
   # Найди DATABASE_URL и REDIS_URL, они должны быть заполнены
   ```

---

## Лимиты Railway (бесплатный план)

- ✅ 500 часов работы в месяц (~20 дней 24/7)
- ✅ $5 кредита в месяц
- ✅ Неограниченные деплои
- ✅ PostgreSQL 1 ГБ
- ✅ Redis 100 МБ

**Этого хватит** для тестирования и небольшого числа пользователей.

---

## Альтернатива: Деплой через Docker локально

Если не хочешь Railway, можешь запустить бота на своём компьютере:

```powershell
cd "C:\MainMalbara\Бот для флиппинга"
docker-compose up --build
```

Бот будет работать, пока компьютер включён.

---

**Нужна помощь?** Пиши сюда, помогу с любым шагом!
