import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN

from app.handlers import common, user, admin
from app.db.database import Database

from app.utils.logger import logger

from app.middlewares.auth import AuthMiddleware

# Перевірка змінних середовища
print("🔍 Перевірка змінних середовища...")
print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")
if BOT_TOKEN:
    print(f"BOT_TOKEN length: {len(BOT_TOKEN)}")

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL exists: {bool(DATABASE_URL)}")
if DATABASE_URL:
    # Показуємо тільки початок для безпеки
    print(f"DATABASE_URL starts with: {DATABASE_URL[:15]}...")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# реєстрація всіх роутерів
dp.include_router(common.router)
dp.include_router(user.router)
dp.include_router(admin.router)


async def main():
    print("🚀 Запуск Football Bot...")
    
    db = Database()
    await db.connect()
    dp.message.middleware(AuthMiddleware(db))
    
    print("⚽ Бот готовий до роботи!")
    
    try:
        await dp.start_polling(bot, db=db)
    finally:
        await db.close()
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
