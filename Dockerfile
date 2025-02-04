# Використовуємо Python 3.11
FROM python:3.11

# Створюємо робочу директорію
WORKDIR /app

# Копіюємо файл залежностей
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код у контейнер
COPY . .

# Створюємо порожню папку static, якщо її немає
RUN mkdir -p /app/static

# Відкриваємо порт
EXPOSE 8000

# Запускаємо FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
  