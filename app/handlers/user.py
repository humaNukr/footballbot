from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart

from app.keyboards.reply import start_keyboard, get_main_panel
from app.db.database import Database
from app.db.models import add_user
from app.utils.logger import logger

router = Router()

class RegisterState(StatesGroup):
    waiting_for_name = State()


@router.message(F.text == "Зареєструватися")
async def register_user(message: Message, state: FSMContext, is_registered: bool):
    if is_registered:
        await message.answer("Ви вже зареєстровані ✅")
        return

    await message.answer("Введіть ваше ім'я 📝:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterState.waiting_for_name)

@router.message(RegisterState.waiting_for_name)
async def process_name(message: Message, state: FSMContext, db: Database):
    name = message.text.strip()
    telegram_id = message.from_user.id

    await add_user(
        db=db,
        telegram_id=telegram_id,
        username=message.from_user.username,
        first_name=name,
    )

    await message.answer(f"Дякую, {name}! Ви зареєстровані ✅", reply_markup=get_main_panel(is_registered=True, is_admin=False))
    await state.clear()
