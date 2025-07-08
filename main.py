from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN

from app.handlers import common, user, admin


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# реєстрація всіх роутерів
dp.include_router(common.router)
# dp.include_router(user.router)
# dp.include_router(admin.router)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
