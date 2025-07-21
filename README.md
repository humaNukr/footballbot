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

### Деплой на хостинг 

**🚄 Railway (рекомендовано - БЕЗКОШТОВНО):**
- Детальна інструкція: **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)**
- Background Worker включений в безкоштовний план
- PostgreSQL безкоштовно
- 500 годин/місяць

**🔧 Render (обмежено):**
- Детальна інструкція: **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**  
- Background Worker тільки на платному плані
- Потрібен workaround для безкоштовного

## 🛠️ Функції

- ⚽ **Створення матчів** (адміни)
- 👥 **Реєстрація на матчі** (користувачі)
- 📊 **Статистика** (адміни)
- 💬 **Відгуки** користувачів
- 🗓️ **Календар** для вибору дат
- 🎨 **Динамічний UI** - оновлення без спаму повідомлень

## 📚 Документація

- **[POSTGRES_SETUP.md](POSTGRES_SETUP.md)** - локальне налаштування PostgreSQL
- **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** - 🚄 деплой на Railway (БЕЗКОШТОВНО)
- **[DATABASE_MIGRATION.md](DATABASE_MIGRATION.md)** - 🗃️ міграція існуючої бази даних
- **[UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md)** - 🎨 покращення інтерфейсу користувача
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - 🔧 деплой на Render (обмежено)

## 🗄️ База даних

PostgreSQL з автоматичним створенням таблиць:
- `users` - користувачі бота
- `schedule` - розклад матчів  
- `registrations` - реєстрації на матчі
- `feedback` - відгуки користувачів

## 🔑 Змінні середовища

```bash
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:pass@host:port/db  # для Railway/Render
# АБО для локального запуску:
DB_HOST=localhost
DB_PORT=5432  
DB_USER=football
DB_PASS=footballpass
DB_NAME=football_db

# Для production
RAILWAY=true    # для Railway
RENDER=true     # для Render
```
