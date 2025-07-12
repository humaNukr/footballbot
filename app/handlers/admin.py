from datetime import time, datetime, timedelta
import calendar

from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.handlers.user import RegisterState
from app.middlewares.admin_check import IsAdmin
from app.keyboards.inline import admin_main_menu, admin_users_menu, admin_back, user_action_menu
from app.db.models import (
    get_all_users, get_users_count, get_user_by_id, search_users,
    make_admin, remove_admin, get_admins, get_stats, log_broadcast, add_schedule
)
from app.services.notify import push_calendar_update
from app.states.register import AdminStates
from app.db.database import Database

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

    await log_broadcast(db, broadcast_text)

    result_text = f"""📢 <b>Розсилка завершена!</b>
    
✅ Успішно надіслано:  <b>{success_count}</b>"""

    await message.answer(result_text, reply_markup=admin_main_menu())
    await state.clear()


def create_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    """Створює календар для вибору дати"""
    import pytz
    kyiv_tz = pytz.timezone('Europe/Kiev')
    today = datetime.now(kyiv_tz)
    
    # Назви місяців українською
    months = [
        "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
        "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
    ]
    
    # Створюємо календар
    keyboard = []
    
    # Заголовок з місяцем та роком
    keyboard.append([
        InlineKeyboardButton(
            text=f"{months[month-1]} {year}", 
            callback_data="ignore"
        )
    ])
    
    # Дні тижня
    keyboard.append([
        InlineKeyboardButton(text="Пн", callback_data="ignore"),
        InlineKeyboardButton(text="Вт", callback_data="ignore"),
        InlineKeyboardButton(text="Ср", callback_data="ignore"),
        InlineKeyboardButton(text="Чт", callback_data="ignore"),
        InlineKeyboardButton(text="Пт", callback_data="ignore"),
        InlineKeyboardButton(text="Сб", callback_data="ignore"),
        InlineKeyboardButton(text="Нд", callback_data="ignore"),
    ])
    
    # Отримуємо календар для місяця
    month_calendar = calendar.monthcalendar(year, month)
    
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                # Перевіряємо, чи дата не в минулому
                date_obj = datetime(year, month, day)
                if date_obj < today.replace(hour=0, minute=0, second=0, microsecond=0):
                    row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
                else:
                    row.append(InlineKeyboardButton(
                        text=str(day), 
                        callback_data=f"calendar_day_{year}_{month}_{day}"
                    ))
        keyboard.append(row)
    
    # Кнопки навігації
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
        
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1
    
    keyboard.append([
        InlineKeyboardButton(
            text="◀️", 
            callback_data=f"calendar_prev_{prev_year}_{prev_month}"
        ),
        InlineKeyboardButton(
            text="🔙 Назад", 
            callback_data="admin_back"
        ),
        InlineKeyboardButton(
            text="▶️", 
            callback_data=f"calendar_next_{next_year}_{next_month}"
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data == "admin_plan_game")
async def admin_game_handler(callback: CallbackQuery, state: FSMContext):
    import pytz
    kyiv_tz = pytz.timezone('Europe/Kiev')
    today = datetime.now(kyiv_tz)
    await callback.message.edit_text(
        "📅 <b>Запланувати гру</b>\n\n"
        "Виберіть дату гри:",
        reply_markup=create_calendar(today.year, today.month)
    )
    await state.set_state(AdminStates.waiting_for_game_date)
    await callback.answer()

@router.callback_query(F.data.startswith("calendar_day_"))
async def process_calendar_day(callback: CallbackQuery, state: FSMContext):
    """Обробка вибору дня"""
    _, _, year, month, day = callback.data.split("_")
    date_obj = datetime(int(year), int(month), int(day))
    
    await state.update_data(game_date=date_obj.strftime("%Y-%m-%d"))
    await callback.message.edit_text(
        f"✅ Вибрана дата: <b>{date_obj.strftime('%d.%m.%Y')}</b>\n\n"
        f"Введіть час гри у форматі ГГ:ХХ (наприклад, 18:30):",
        reply_markup=admin_back()
    )
    await state.set_state(AdminStates.waiting_for_game_time)
    await callback.answer()

@router.callback_query(F.data.startswith("calendar_prev_"))
async def process_calendar_prev(callback: CallbackQuery):
    """Перехід до попереднього місяця"""
    _, _, year, month = callback.data.split("_")
    await callback.message.edit_reply_markup(
        reply_markup=create_calendar(int(year), int(month))
    )
    await callback.answer()

@router.callback_query(F.data.startswith("calendar_next_"))
async def process_calendar_next(callback: CallbackQuery):
    """Перехід до наступного місяця"""
    _, _, year, month = callback.data.split("_")
    await callback.message.edit_reply_markup(
        reply_markup=create_calendar(int(year), int(month))
    )
    await callback.answer()

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    """Ігноруємо неактивні кнопки"""
    await callback.answer()

@router.message(AdminStates.waiting_for_game_time)
async def process_game_time(message: Message, state: FSMContext, db: Database):
    time = message.text.strip()

    try:
        hour, minute = map(int, time.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError

        state_data = await state.get_data()
        game_date = state_data['game_date']
        # Store time in state
        await state.update_data(game_time=f"{hour:02d}:{minute:02d}")

        await message.answer(
            f"✅ Гру заплановано на <b>{game_date}</b> о <b>{time}</b>\n"
            f"Введіть додаткову інформацію для користувачів:",
            reply_markup=admin_back()
        )
        await state.set_state(AdminStates.waiting_for_additional_info)

    except ValueError:
        await message.answer(
            "❌ Некоректний формат часу. Введіть час у форматі ГГ:ХХ (наприклад, 18:30):",
            reply_markup=admin_back()
        )

@router.message(AdminStates.waiting_for_additional_info)
async def process_additional_info(message: Message, state: FSMContext, db: Database):
    additional_info = message.text.strip()
    state_data = await state.get_data()
    game_date = state_data['game_date']
    game_time = state_data['game_time']
    user_id = message.from_user.id

    await add_schedule(db, user_id, game_date, game_time, additional_info)

    await push_calendar_update(message, state, db)

    await message.answer(
        "✅ Гру успішно заплановано!\n"
        f"Дата та час: {game_date} {game_time}\n"
        f"Додаткова інформація: {additional_info}",
        reply_markup=admin_main_menu()
    )

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

@router.callback_query(F.data == "admin_feedbacks", IsAdmin())
async def view_feedbacks(callback: CallbackQuery, db: Database):
    query = """
            SELECT first_name, username, feedback_text, created_at
            FROM feedback
            ORDER BY created_at DESC
            """
    feedbacks = await db.fetchall(query)

    if not feedbacks:
        await callback.message.answer("📭 Відгуків ще немає.")
        return

    text = "<b>💬 Останні відгуки користувачів:</b>\n\n"
    for first_name, username, fb_text, created_at in feedbacks:
        text += (
            f"👤 <b>{first_name}</b> (@{username})\n"
            f"🕒 {created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"💬 {fb_text}\n\n"
        )

    await callback.message.answer(text, reply_markup=admin_back())
