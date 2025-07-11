from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.handlers.user import RegisterState
from app.middlewares.admin_check import IsAdmin
from app.keyboards.inline import admin_main_menu, admin_users_menu, admin_back, user_action_menu
from app.db.models import (
    get_all_users, get_users_count, get_user_by_id, search_users,
    make_admin, remove_admin, get_admins, get_stats
)
from app.states.register import AdminStates
from app.db.database import Database
from app.db.models import save_feedback

router = Router()

router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

@router.message(F.text == "/admin")
async def admin_menu(message: Message):
    await message.answer(
        "🔐 <b>Адмін-панель</b>\n\n"
        "Виберіть дію:",
        reply_markup=admin_main_menu()
    )

# Головне меню адміна
@router.callback_query(F.data == "admin_back")
async def admin_back_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔐 <b>Адмін-панель</b>\n\n"
        "Виберіть дію:",
        reply_markup=admin_main_menu()
    )
    await callback.answer()

# Управління користувачами
@router.callback_query(F.data == "admin_users")
async def admin_users_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "👥 <b>Управління користувачами</b>\n\n"
        "Виберіть дію:",
        reply_markup=admin_users_menu()
    )
    await callback.answer()

# Список користувачів
@router.callback_query(F.data == "admin_user_list")
async def admin_user_list_handler(callback: CallbackQuery, db: Database):
    users = await get_all_users(db)
    total_count = await get_users_count(db)
    
    if not users:
        await callback.message.edit_text(
            "📋 <b>Список користувачів порожній</b>",
            reply_markup=admin_back()
        )
        await callback.answer()
        return
    
    text = f"📋 <b>Список користувачів</b>\n\n"
    
    for user in users:
        telegram_id, username, first_name, is_admin, registered_at = user
        admin_badge = " 👑" if is_admin else ""
        username_text = f"@{username}" if username else "—"
        text += f"  Name: <b>{first_name}</b>{admin_badge}\n"
        text += f"  ID: <code>{telegram_id}</code>\n"
        text += f"  Username: {username_text}\n\n"
    
    await callback.message.edit_text(text, reply_markup=admin_back())
    await callback.answer()

# Пошук користувача
@router.callback_query(F.data == "admin_user_search")
async def admin_user_search_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 <b>Пошук користувача</b>\n\n"
        "Введіть ім'я або username користувача:",
        reply_markup=admin_back()
    )
    await state.set_state(AdminStates.waiting_for_user_search)
    await callback.answer()

@router.message(AdminStates.waiting_for_user_search)
async def process_user_search(message: Message, state: FSMContext, db: Database):
    search_term = message.text.strip()
    users = await search_users(db, search_term)
    
    if not users:
        await message.answer(
            f"🔍 За запитом '<b>{search_term}</b>' нічого не знайдено",
            reply_markup=admin_back()
        )
        await state.clear()
        return
    
    text = f"🔍 <b>Результати пошуку:</b> '{search_term}'\n\n"
    
    for user in users:
        telegram_id, username, first_name, is_admin, registered_at = user
        admin_badge = " 👑" if is_admin else ""
        username_text = f"@{username}" if username else "—"
        text += f"  Name: <b>{first_name}</b>{admin_badge}\n"
        text += f"  ID: <code>{telegram_id}</code>\n"
        text += f"  Username: {username_text}\n\n"
    
    await message.answer(text, reply_markup=admin_back())
    await state.clear()

# Додати адміна
@router.callback_query(F.data == "admin_add_admin")
async def admin_add_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "👑 <b>Додати адміна</b>\n\n"
        "Введіть Telegram ID користувача, якого хочете зробити адміном:",
        reply_markup=admin_back()
    )
    await state.set_state(AdminStates.waiting_for_admin_id)
    await callback.answer()

@router.message(AdminStates.waiting_for_admin_id)
async def process_add_admin(message: Message, state: FSMContext, db: Database):
    telegram_id = message.text.strip()

    try:
        telegram_id = int(telegram_id)
        user = await get_user_by_id(db, telegram_id)

        if not user:
            await message.answer("❌ Користувача з таким ID не знайдено!", reply_markup=admin_back())
            await state.clear()
            return

        await make_admin(db, telegram_id)
        await message.answer("✅ Адмін успішно доданий!", reply_markup=admin_back())

    except ValueError:
        await message.answer("❌ ID повинен бути числом!", reply_markup=admin_back())

    await state.clear()

# Видалити адміна
@router.callback_query(F.data == "admin_remove_admin")
async def admin_remove_admin_handler(callback: CallbackQuery, db: Database, state: FSMContext):
    admins = await get_admins(db)
    
    if len(admins) <= 1:
        await callback.message.edit_text(
            "⚠️ <b>Неможливо видалити адміна</b>\n\n"
            "Повинен залишитися хоча б один адмін",
            reply_markup=admin_back()
        )
        await callback.answer()
        return
    
    text = "❌ <b>Список адмінів:</b>\n\n"
    for admin in admins:
        telegram_id, username, first_name = admin
        username_text = f"@{username}" if username else "—"
        text += f" <b>{first_name}</b>\n"
        text += f"  ID: <code>{telegram_id}</code>\n"
        text += f"  Username: {username_text}\n\n"
    
    text += "Введіть ID адміна, якого хочете видалити:"
    
    await callback.message.edit_text(text, reply_markup=admin_back())
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_remove_admin_id)



@router.message(AdminStates.waiting_for_remove_admin_id)
async def  delete_admin(message: Message,state: FSMContext, db : Database):
    telegram_id = message.text.strip()

    try:
        telegram_id = int(telegram_id)
        user = await get_user_by_id(db, telegram_id)

        if not user:
            await message.answer("❌ Користувача з таким ID не знайдено!", reply_markup=admin_back())
            await state.clear()
            return

        await remove_admin(db, telegram_id)
        await message.answer("✅ Адмін успішно видалений!", reply_markup=admin_back())

    except ValueError:
        await message.answer("❌ ID повинен бути числом!", reply_markup=admin_back())

    await state.clear()


@router.callback_query(F.data == "admin_stats", IsAdmin())
async def admin_stats(callback: CallbackQuery, db: Database):
    stats = await get_stats(db)

    text = (
        "<b>📊 Статистика </b>\n\n"
        f"👤 Загальна кількість користувачів: <b>{stats['total_users']}</b>\n"
        f"🛡️ Адміністраторів: <b>{stats['total_admins']}</b>\n"
        f"📅 Нових сьогодні: <b>{stats['today_users']}</b>\n"
        f"💬 Кількість відгуків: <b>{stats['feedbacks']}</b>"
    )

    await callback.message.edit_text(text, reply_markup=admin_back())
    await callback.answer()


# Розсилка
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 <b>Розсилка повідомлення</b>\n\n"
        "Введіть текст повідомлення для розсилки всім користувачам:",
        reply_markup=admin_back()
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await callback.answer()

@router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast(message: Message, state: FSMContext, db: Database):
    broadcast_text = message.text
    users = await get_all_users(db)

    non_admin_users = [user for user in users if not user[3]]

    if not users:
        await message.answer("❌ Немає користувачів для розсилки.", reply_markup=admin_back())
        await state.clear()
        return

    success_count = 0
    failed_count = 0

    for user in non_admin_users:
        telegram_id = user[0]
        try:
            await message.bot.send_message(telegram_id, broadcast_text)
            success_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to send message to {telegram_id}: {e}")
            failed_count += 1

    result_text = f"""📢 <b>Розсилка завершена!</b>
    
✅ Успішно надіслано:  <b>{success_count}</b>"""

    await message.answer(result_text, reply_markup=admin_main_menu())
    await state.clear()


# Налаштування
@router.callback_query(F.data == "admin_settings")
async def admin_settings_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ <b>Налаштування</b>\n\n"
        "Цей розділ в розробці...",
        reply_markup=admin_back()
    )
    await callback.answer()
