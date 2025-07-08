@echo off
:: Створення Dockerfile
(
echo # 1. Базовий образ
echo FROM python:3.11-slim
echo.
echo # 2. Робоча директорія
echo WORKDIR /usr/src/app
echo.
echo # 3. Копіюємо залежності
echo COPY requirements.txt .
echo.
echo # 4. Встановлюємо
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo # 5. Копіюємо код
echo COPY . .
echo.
echo # 6. Команда запуску
echo CMD ["python", "main.py"]
) > Dockerfile

:: Створення docker-compose.yml
(
echo version: "3.8"
echo.
echo services:
echo   db:
echo     image: mysql:8
echo     container_name: football_mysql
echo     restart: always
echo     environment:
echo       MYSQL_ROOT_PASSWORD: rootpass
echo       MYSQL_DATABASE: users_db
echo       MYSQL_USER: football
echo       MYSQL_PASSWORD: footballpass
echo     ports:
echo       - "3306:3306"
echo     volumes:
echo       - db_data:/var/lib/mysql
echo.
echo   bot:
echo     build: .
echo     container_name: football_bot
echo     restart: always
echo     depends_on:
echo       - db
echo     environment:
echo       - BOT_TOKEN=${BOT_TOKEN}
echo       - DB_HOST=db
echo       - DB_USER=football
echo       - DB_PASS=footballpass
echo       - DB_NAME=users_db
echo     volumes:
echo       - .:/usr/src/app
echo.
echo volumes:
echo   db_data:
) > docker-compose.yml

echo Файли успішно створені: Dockerfile та docker-compose.yml
pause
