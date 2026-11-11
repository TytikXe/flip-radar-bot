# 🔑 СОЗДАНИЕ GITHUB РЕПОЗИТОРИЯ ДЛЯ @TytikXe

## Шаг 1: Создать репозиторий на GitHub

1. Открой https://github.com/new
2. **Войди под аккаунтом `TytikXe`**
3. Заполни форму:
   - **Repository name**: `flip-radar-bot`
   - **Description**: `Telegram bot for NFT gift flipping with 3 trading modes`
   - **Visibility**: **Public** (чтобы Railway мог подключиться бесплатно)
   - **Initialize**: НЕ ставь галочки (README, .gitignore, license)
4. Нажми **"Create repository"**

---

## Шаг 2: Скопировать команды из GitHub

GitHub покажет страницу с инструкциями. **Скопируй URL репозитория:**

```
https://github.com/TytikXe/flip-radar-bot.git
```

---

## Шаг 3: Запушить код в GitHub

Открой PowerShell и выполни:

```powershell
cd "C:\MainMalbara\Бот для флиппинга"

# Добавить remote репозиторий
git remote add origin https://github.com/TytikXe/flip-radar-bot.git

# Запушить код
git push -u origin main
```

**GitHub попросит авторизацию:**
- Username: `TytikXe`
- Password: **Personal Access Token** (не пароль!)

---

## Шаг 2.5: Создать Personal Access Token (если ещё нет)

1. Открой https://github.com/settings/tokens
2. Нажми **"Generate new token (classic)"**
3. Заполни:
   - **Note**: `Railway deployment`
   - **Expiration**: `No expiration`
   - **Scopes**: поставь галочку **`repo`**
4. Нажми **"Generate token"**
5. **СКОПИРУЙ ТОКЕН** (он больше не появится!)
6. Используй токен как пароль при `git push`

---

## Шаг 4: Подключить Railway к GitHub

1. Открой https://railway.app → **Login with GitHub**
2. Нажми **"New Project"**
3. Выбери **"Deploy from GitHub repo"**
4. Выбери **`TytikXe/flip-radar-bot`**
5. Railway автоматически:
   - Обнаружит `docker-compose.yml`
   - Создаст 3 сервиса: `bot`, `db`, `redis`
   - Запустит деплой

---

## Шаг 5: Настроить переменные в Railway

1. Railway → проект → сервис **`bot`** → вкладка **"Variables"**
2. Нажми **"Raw Editor"**
3. Вставь:

```env
BOT_TOKEN=9054803178:AAEzqn1M4d2iZFDM6yfqEBAmeEN8Bqfgu5E
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
ENVIRONMENT=production
LOG_LEVEL=INFO
```

4. Нажми **"Update Variables"**
5. Railway автоматически перезапустит бота

---

## Шаг 6: Проверить логи

Railway → сервис `bot` → вкладка **"Deployments"** → **"View Logs"**

Должен увидеть:
```
INFO: Бот запущен
INFO: Polling started
```

---

## Шаг 7: Проверить в Telegram

1. Открой Telegram
2. Найди бота через поиск
3. Отправь `/start`
4. Должен ответить с выбором профиля

---

## 🎉 ГОТОВО!

Бот работает 24/7 на Railway, код в GitHub.

---

## Управление после деплоя

### Обновить код:
```powershell
cd "C:\MainMalbara\Бот для флиппинга"

# Внести изменения в файлы
# Затем:
git add .
git commit -m "Update bot code"
git push origin main
```

Railway автоматически задеплоит новую версию.

### Посмотреть статус:
https://railway.app → Проект → Deployments

### Остановить бота:
Railway → сервис `bot` → Settings → **"Remove Service"**

---

## Проблемы и решения

### Ошибка: "remote: Repository not found"
**Решение:** Проверь, что репозиторий создан и URL правильный.

### Ошибка: "Authentication failed"
**Решение:** Используй Personal Access Token вместо пароля.

### Ошибка: "DATABASE_URL not set"
**Решение:** Railway → Variables → убедись, что `${{Postgres.DATABASE_URL}}` подставлен автоматически.

---

**Следуй шагам по порядку → бот заработает!**
