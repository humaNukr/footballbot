from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.db.database import Database
from app.db.models import log_broadcast, get_all_users, get_admins
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


async def push_feedback_update(message: Message, state: FSMContext, db: Database):
    feedback_text = "✏️ Додано новий відгук!"
    admins = await get_admins(db)

    if not admins:
        await state.clear()
        return

    for user in admins:
        telegram_id = user[0]
        try:
            await message.bot.send_message(telegram_id, feedback_text)
        except Exception as e:
            print(f"[ERROR] Failed to send message to {telegram_id}: {e}")
    await state.clear()


async def push_users_db_update(message: Message, state: FSMContext, db: Database,
                               telegram_id=None, username=None, first_name=None):

    admins = await get_admins(db)

    register_text = ("👤 Новий користувач зареєстрований! Його дані: \n\n"
                     "ID: <code>{telegram_id}</code>\n"
                     "Username: @{username}\n"
                     "First name: {first_name}").format(telegram_id=telegram_id, username=username, first_name=first_name)

    if not admins:
        await state.clear()
        return

    for user in admins:
        telegram_id = user[0]
        try:
            await message.bot.send_message(telegram_id, register_text)
        except Exception as e:
            print(f"[ERROR] Failed to send message to {telegram_id}: {e}")
    await state.clear()