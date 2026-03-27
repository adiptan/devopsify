FROM python:3.12-slim

WORKDIR /app

# Копировать зависимости
COPY requirements.txt .

# Установить зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копировать код бота
COPY bot/ ./bot/

# Копировать тесты
COPY tests/ ./tests/

# Создать директорию для БД
RUN mkdir -p /app/data

# Запуск бота
CMD ["python", "-m", "bot.main"]
