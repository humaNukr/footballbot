# PostgreSQL Setup для Football Bot

## Зміни в коді

Код було повністю переписано для роботи з PostgreSQL замість MySQL.

### Основні зміни:

1. **Database Driver**: `aiomysql` → `asyncpg`
2. **SQL Syntax**: MySQL → PostgreSQL
3. **Docker**: MySQL → PostgreSQL + pgAdmin
4. **Environment Variables**: оновлені для PostgreSQL

## Налаштування .env файлу

Створіть `.env` файл з наступними параметрами:

```bash
BOT_TOKEN=your_bot_token_here

# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=football
DB_PASS=footballpass
DB_NAME=football_db
```

## Запуск з Docker

```bash
# Побудова та запуск контейнерів
docker-compose up --build -d

# Перегляд логів
docker-compose logs -f bot

# Зупинка
docker-compose down
```

## Доступ до бази даних

- **pgAdmin**: http://localhost:8080
  - Email: admin@admin.com
  - Password: admin

Після входу в pgAdmin:
1. Add New Server
2. Host: db
3. Port: 5432
4. Database: football_db
5. Username: football
6. Password: footballpass

## Автоматичні налаштування

База даних та таблиці створюються автоматично при першому запуску.

## Основні відмінності PostgreSQL від MySQL

1. **Placeholders**: `$1, $2, $3` замість `%s, %s, %s`
2. **ON CONFLICT**: замість `ON DUPLICATE KEY UPDATE`
3. **SERIAL**: замість `AUTO_INCREMENT`
4. **CURRENT_DATE**: замість `CURRENT_DATE()`
5. **TIMESTAMPTZ**: timezone-aware timestamps
6. **ILIKE**: case-insensitive LIKE 