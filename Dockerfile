# 1. Базовый образ
FROM python:3.11-slim

# 2. Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем исходники
COPY . .

# 4. Указываем команду запуска
CMD ["python", "run.py"]
