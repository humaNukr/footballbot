from aiogram import Router, F
from aiogram.types import Message
from app.middlewares.admin_check import IsAdmin

router = Router()

router.message.filter(IsAdmin())

@router.message(F.text == "/admin")
async def admin_menu(message: Message):
    await message.answer("🔐 Адмін-панель активна.")
