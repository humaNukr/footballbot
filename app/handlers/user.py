from aiogram import Router, types
from aiogram.types import Message

from app.db.models import add_user
from aiogram import F

router = Router()


@router.message(F.text == "Зареєструватися")
async def register_user(message: Message):
    await add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    await message.answer("Привіт! Вас зареєстровано ✅")
