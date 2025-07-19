# Football Bot ⚽

Telegram бот для організації футбольних матчів з автоматичними нагадуваннями.

## 🚀 Швидкий старт

### Локальний запуск (Docker)
```bash
# 1. Створити .env файл з BOT_TOKEN
echo "BOT_TOKEN=your_bot_token" > .env

# 2. Запустити з PostgreSQL
docker-compose up --build -d

# 3. Перевірити логи
docker-compose logs -f bot
```

### Деплой на Render 
Детальна інструкція: **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

1. Створити GitHub репозиторій
2. Створити PostgreSQL на render.com
3. Створити Web Service на render.com
4. Налаштувати змінні: `BOT_TOKEN`, `DATABASE_URL`, `RENDER=true`

## 🛠️ Функції

- ⚽ **Створення матчів** (адміни)
- 👥 **Реєстрація на матчі** (користувачі)
- 📊 **Статистика** (адміни)
- 💬 **Відгуки** користувачів
- 🗓️ **Календар** для вибору дат

## 📚 Документація

- **[POSTGRES_SETUP.md](POSTGRES_SETUP.md)** - локальне налаштування PostgreSQL
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - деплой на хостинг

## 🗄️ База даних

PostgreSQL з автоматичним створенням таблиць:
- `users` - користувачі бота
- `schedule` - розклад матчів  
- `registrations` - реєстрації на матчі
- `feedback` - відгуки користувачів

## 🔑 Змінні середовища

```bash
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:pass@host:port/db  # для Render
# АБО для локального запуску:
DB_HOST=localhost
DB_PORT=5432  
DB_USER=football
DB_PASS=footballpass
DB_NAME=football_db
```
