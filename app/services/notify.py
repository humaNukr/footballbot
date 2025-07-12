from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.db.database import Database
from app.db.models import log_broadcast, get_all_users
from app.keyboards.inline import admin_back, admin_main_menu


async def push_calendar_update(message: Message, state: FSMContext, db: Database):
    broadcast_text = "📅 Додано новий розклад ігор! 😍"
    users = await get_all_users(db)

    non_admin_users = [user for user in users if not user[3]]

    if not users:
        await state.clear()
        return

    failed_count = 0

    for user in non_admin_users:
        telegram_id = user[0]
        try:
            await message.bot.send_message(telegram_id, broadcast_text)
        except Exception as e:
            print(f"[ERROR] Failed to send message to {telegram_id}: {e}")
            failed_count += 1

    result_text = "✅ <b>Успішно надіслано повідомлення про оновлення розкладу!</b>"

    await message.answer(result_text)
    await state.clear()