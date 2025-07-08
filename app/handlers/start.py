from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Start")],
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Привіт! Натисни <b>Start</b>, щоб розпочати ⚽",
        reply_markup=keyboard
    )
