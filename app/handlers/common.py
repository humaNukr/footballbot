from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.keyboards.reply import start_keyboard
from app.keyboards.reply import main_panel

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Підтвердіть, що ви погоджуєтеся з політикою конфіденційності ⚽",
        reply_markup=start_keyboard
    )

@router.message(F.text == "🚀 Погоджуюся")
async def process_start_button(message: Message):
    await message.answer(
        "Виберіть одну з опцій:",
        reply_markup=main_panel
        
    )


@router.message(F.text == "Зареєструватися")
async def register_handler(message: Message):
    await message.answer("Ти зареєстрований ✅")

@router.message(F.text == "FAQ")
async def faq_handler(message: Message):
    await message.answer("Це список найчастіших питань ❓")