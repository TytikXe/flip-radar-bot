FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt ./

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Применение миграций и запуск бота
CMD sh -c "alembic upgrade head && python src/bot/main.py"
