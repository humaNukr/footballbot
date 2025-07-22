# 1. Базовий образ
FROM python:3.11-slim

# 2. Встановлюємо системні залежності для MySQL
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Робоча директорія
WORKDIR /usr/src/app

# 4. Копіюємо залежності
COPY requirements.txt .

# 5. Встановлюємо Python пакети
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копіюємо код
COPY . .

# 7. Команда запуску
CMD ["python", "main.py"]
