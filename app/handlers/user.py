from aiogram import Router, types
from aiogram.types import Message

from app.db.models import add_user
from app.db.database import Database
from aiogram import F

router = Router()


@router.message(F.text == "Зареєструватися")
async def register_user(message: Message, db: Database):
    await add_user(
        db=db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    await message.answer("Привіт! Вас зареєстровано ✅")
