# Деплой Football Bot на Render

## 🚀 Пошагова інструкція деплою

### 1. Підготовка GitHub репозиторію

```bash
# Додати всі файли до git
git add .
git commit -m "Add Render deployment support"
git push origin main
```

### 2. Створення бази даних на Render

1. Зайдіть на [render.com](https://render.com) і увійдіть в акаунт
2. Натисніть **"New +"** → **"PostgreSQL"**
3. Налаштування:
   - **Name**: `football-postgres`
   - **Database**: `football_db`
   - **User**: `football`
   - **Region**: ближче до вас
   - **Plan**: Free
4. Натисніть **"Create Database"**
5. **Збережіть DATABASE_URL** (буде потрібно пізніше)

### 3. Створення Background Worker

1. Натисніть **"New +"** → **"Background Worker"**
2. Підключіть ваш GitHub репозиторій
3. Налаштування:
   - **Name**: `football-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free

> ⚠️ **Важливо**: Обов'язково оберіть **Background Worker**, а не Web Service! Telegram боти не потребують веб-портів.

### 4. Налаштування змінних середовища

В розділі **Environment Variables** додайте:

```
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=postgresql://username:password@host:port/database
RENDER=true
```

**Важливо**: DATABASE_URL беріть з розділу "Connect" вашої бази даних.

### 5. Автоматичний деплой (опціонально)

Якщо ви хочете автоматичний деплой:

1. Додайте файл `render.yaml` в корінь проекту (вже створений)
2. В Render Dashboard → Settings → Build & Deploy
3. Увімкніть **"Auto-Deploy"**

## 🔧 Особливості конфігурації

### SSL з'єднання
Код автоматично додає SSL для production середовища:
```python
if DATABASE_URL or os.getenv("RENDER"):
    connection_params["ssl"] = "require"
```

### Підтримка DATABASE_URL
Код підтримує як окремі змінні, так і DATABASE_URL:
```python
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Парсинг URL для Render
    url = urlparse(DATABASE_URL)
    # ...
```

## 📊 Моніторинг та логи

### Перегляд логів
1. Render Dashboard → ваш Background Worker → Logs
2. Або через CLI: `render logs -s football-bot`

### Важливі логи для перевірки:
```
✅ Connected to PostgreSQL DB!
✅ Database tables created/updated
```

## 🛠️ Тестування після деплою

### 1. Основне тестування
- Надішліть `/start` боту
- Перевірте, чи працює реєстрація
- Спробуйте створити матч (якщо ви адмін)



### 2. Перевірка бази даних
- Зайдіть в Render Dashboard → PostgreSQL
- Використовуйте "External Connection" для підключення через pgAdmin

## ⚠️ Важливі примітки

### Безкоштовний план Render
- **Обмеження**: 750 годин на місяць
- **Сплячий режим**: після 15 хв неактивності
- **Пробудження**: ~30 секунд при першому запиті

### Рекомендації для production:
1. **Платний план** для 24/7 роботи
2. **Backup бази даних** регулярно
3. **Моніторинг логів** на помилки
4. **Health check** endpoint (можна додати)

## 🔄 Оновлення коду

Після push в GitHub:
```bash
git add .
git commit -m "Update bot features"
git push origin main
```

Render автоматично передеплоїть сервіс (якщо увімкнений Auto-Deploy).

## 🆘 Troubleshooting

### Проблема: "No open ports detected" / "Port scan timeout"
```bash
# Render очікує відкритий порт, але Telegram бот його не потребує
# Рішення:
1. Видаліть поточний сервіс якщо створили Web Service
2. Створіть новий Background Worker (не Web Service!)
3. Background Worker не потребує портів - ідеально для ботів
```

### Проблема: "Token is invalid!"
```bash
# Найчастіша помилка при деплої
# Рішення:
1. Перевірте BOT_TOKEN в Environment Variables
2. Переконайтеся, що токен скопійований повністю (без пробілів)
3. Створіть новий токен через @BotFather якщо потрібно
4. Перезапустіть сервіс після зміни токену
```

### Проблема: "Connection failed"
```bash
# Перевірте DATABASE_URL в Environment Variables
# Переконайтеся, що база даних запущена
```

### Проблема: "SSL required"
```bash
# Додайте змінну RENDER=true
# Перезапустіть сервіс
```

### Проблема: "Module not found"
```bash
# Перевірте requirements.txt
# Переконайтеся, що всі залежності вказані
```

## 📱 Налаштування webhook (опціонально)

Для кращої продуктивності можна налаштувати webhook замість polling:

1. В коді замініть `dp.start_polling()` на `dp.start_webhook()`
2. Налаштуйте webhook URL в Telegram Bot API
3. Додайте обробку webhook в Flask/FastAPI

---

**Готово!** Ваш бот тепер працює на Render 24/7! 🎉 