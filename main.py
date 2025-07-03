from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def start_handler(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Зареєструватися")]
        ],
        resize_keyboard=True
    )
    await message.answer("Привіт! Це твій футбольний бот ⚽\nНатисни кнопку для реєстрації:", reply_markup=keyboard)

if __name__ == "__main__":
    import asyncio

    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())
