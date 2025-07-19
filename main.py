from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN

from app.handlers import common, user, admin
from app.db.database import Database

from app.utils.logger import logger

from app.middlewares.auth import AuthMiddleware

import os

# Детальна перевірка токену
print("🔍 Checking environment variables...")
print(f"BOT_TOKEN exists: {BOT_TOKEN is not None}")
print(f"BOT_TOKEN length: {len(BOT_TOKEN) if BOT_TOKEN else 0}")

if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here" or len(BOT_TOKEN.strip()) < 40:
    print("❌ ERROR: BOT_TOKEN не встановлений правильно!")
    print("📋 Перевірте Environment Variables:")
    print("   - BOT_TOKEN повинен бути довжиною ~45-50 символів")
    print("   - Формат: 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh")
    print("   - Отримайте новий токен від @BotFather якщо потрібно")
    exit(1)

# Перевірка DATABASE_URL
database_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL exists: {database_url is not None}")
if database_url:
    print(f"DATABASE_URL starts with: {database_url[:20]}...")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# реєстрація всіх роутерів
dp.include_router(common.router)
dp.include_router(user.router)
dp.include_router(admin.router)


async def main():
    print("🚀 Starting Football Bot...")
    
    db = Database()
    await db.connect()
    dp.message.middleware(AuthMiddleware(db))
    
    try:
        print("✅ Bot connected successfully!")
        await dp.start_polling(bot, db=db)
    finally:
        await db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
