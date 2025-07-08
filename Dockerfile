# 1. Базовий образ
FROM python:3.11-slim

# 2. Робоча директорія
WORKDIR /usr/src/app

# 3. Копіюємо залежності
COPY requirements.txt .

# 4. Встановлюємо
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копіюємо код
COPY . .

# 6. Команда запуску
CMD ["python", "main.py"]
