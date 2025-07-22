from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyexpat.errors import messages

from app.db.database import Database
from app.keyboards.inline import faq_main_menu
from app.db.models import add_user, save_feedback

from app.keyboards.inline import back_to_menu
from app.keyboards.reply import start_keyboard

from app.keyboards.reply import get_main_panel
from app.services.notify import push_feedback_update
from app.states.register import FeedbackStates, GameStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Підтвердіть, що ви погоджуєтеся з політикою конфіденційності ⚽",
        reply_markup=start_keyboard
    )


@router.message(F.text == "🚀 Погоджуюся")
async def process_start_button(message: Message, is_registered: bool, is_admin: bool):
    await message.answer(
        "Виберіть одну з опцій:",
        reply_markup=get_main_panel(is_registered, is_admin)
    )


# FAQ LOGIC
@router.message(F.text == "❓ FAQ")
async def show_faq_menu(message: Message):
    await message.answer(
        "Це розділи найчастіших питань ❗")

    keyboard = faq_main_menu()

    await message.answer("❓ <b>Вибери розділ:</b>", reply_markup=keyboard)


# Відповіді на callback-и
@router.callback_query(F.data == "faq_about")
async def faq_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "🤖 <b>Для чого цей бот?</b>\n\n"
        "Щоб автоматично організовувати футбольні матчі. "
        "Бот розсилає повідомлення, отримує відповіді і рахує кількість учасників.",
        reply_markup=back_to_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "faq_matches")
async def faq_matches(callback: CallbackQuery):
    await callback.message.edit_text(
        "📅 <b>Коли буде наступна гра?</b>\n\n"
        "Адміністратор сам вирішує і запускає розсилку. Ви отримаєте повідомлення і зможете підтвердити участь.",
        reply_markup=back_to_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "faq_admin")
async def faq_admin(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🛠️ <b>Хочете щось запропонувати або повідомити про баг</b>\n\n"
        "Напиши своє повідомлення знизу",
        reply_markup=back_to_menu()
    )
    await state.set_state(FeedbackStates.waiting_for_text)
    await callback.answer()


@router.callback_query(F.data == "faq_back")
async def faq_back(callback: CallbackQuery):
    keyboard = faq_main_menu()
    await callback.message.edit_text("❓ <b>Вибери розділ:</b>", reply_markup=keyboard)
    await callback.answer()


# ADMIN LOGIC
@router.message(F.text == "🔐 Адмін-панель")
async def admin_panel_button(message: Message, is_admin: bool):
    from app.keyboards.inline import admin_main_menu
    await message.answer(
        "🔐 <b>Адмін-панель</b>\n\n"
        "Виберіть дію:",
        reply_markup=admin_main_menu()
    )


@router.message(F.text == "💬 Залишити відгук")
async def start_feedback(message: Message, state: FSMContext):
    await message.answer("📝 Напишіть свій відгук у наступному повідомленні:")
    await state.set_state(FeedbackStates.waiting_for_text)


@router.message(FeedbackStates.waiting_for_text)
async def process_feedback_text(message: Message, state: FSMContext, db: Database):
    feedback_text = message.text.strip()

    if not feedback_text:
        await message.answer("❗️ Відгук не може бути порожнім. Спробуйте ще раз.")
        return

    user_id = message.from_user.id

    try:
        await save_feedback(db, user_id, feedback_text)
        await push_feedback_update(message, state, db)
        await message.answer("✅ Дякуємо за ваше повідомлення. Адмін прочитає це незабаром!")
    except Exception as e:
        await message.answer("❌ Помилка під час збереження відгуку.")
        print(f"[FEEDBACK ERROR] {e}")

    await state.clear()


@router.message(F.text == "📅 Розклад")
async def show_schedule(message: Message, db: Database, is_admin: bool = False):
    # Автоматично видаляємо старі матчі
    await db.execute("DELETE FROM schedule WHERE date < CURRENT_DATE")

    query = """
            SELECT s.id, s.first_name, s.date, s.time, s.message
            FROM schedule s
            ORDER BY s.date, s.time \
            """
    result = await db.fetchall(query)

    if not result:
        await message.answer(
            "📭 <b>Розклад поки що порожній</b>\n\n"
            "🔔 Ви отримаєте повідомлення, коли адмін додасть новий матч!\n\n"
            "⚽ Готуйтеся до гри!"
        )
        return

    from datetime import datetime
    matches_by_date = {}
    for row in result:
        match_id, first_name, date, time_, msg = row
        date_key = str(date)
        if date_key not in matches_by_date:
            matches_by_date[date_key] = []
        matches_by_date[date_key].append((match_id, first_name, date, time_, msg))

    match_count = 0
    for date_key, matches in matches_by_date.items():
        try:
            date_obj = datetime.strptime(date_key, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            day_name = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"][date_obj.weekday()]
        except:
            formatted_date = date_key
            day_name = ""

        for match_id, first_name, date, time_, msg in matches:
            match_count += 1
            text = (
                f"🎯 <b>Матч #{match_count}</b>\n"
                f"📅 <b>Дата:</b> {formatted_date} ({day_name})\n"
                f"🕐 <b>Час:</b> {time_}\n"
                f"👨‍💼 <b>Організатор:</b> {first_name}\n"
                f"📋 <b>Деталі:</b> {msg}\n"
                f"⚡  <i>Натисніть, щоб записатися 👇</i>\n"
                f"🔥 <i>Футбол - це життя!</i> 🔥"
            )

            keyboard_buttons = [
                [
                    InlineKeyboardButton(text="✅ Прийду", callback_data=f"register_match:{match_id}"),
                    InlineKeyboardButton(text="❌ Не прийду", callback_data=f"unregister_match:{match_id}"),
                ],
                [
                    InlineKeyboardButton(text="👥 Учасники", callback_data=f"match_participants:{match_id}")
                ]
            ]
            if is_admin:
                keyboard_buttons.append([
                    InlineKeyboardButton(text="🗑️ Видалити цей матч", callback_data=f"delete_match:{match_id}")
                ])
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("register_match:"))
async def register_to_match(callback: CallbackQuery, db: Database):
    match_id = int(callback.data.split(":")[1])
    telegram_id = callback.from_user.id
    username = callback.from_user.username

    try:
        query_user = "SELECT first_name FROM users WHERE telegram_id = %s"
        result = await db.fetchone(query_user, (telegram_id,))

        if not result:
            await callback.answer("❌ Ви не зареєстровані в системі.", )
            return

        first_name = result[0]

        insert_query = """
                       INSERT INTO registrations (match_id, telegram_id, first_name, username)
                       VALUES (%s, %s, %s, %s) AS new_reg
                       ON DUPLICATE KEY UPDATE 
                       first_name = new_reg.first_name, 
                       username = new_reg.username
                       """
        await db.execute(insert_query, (match_id, telegram_id, first_name, username))

        await callback.answer("✅ Ви успішно записалися на матч!")

    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            await callback.answer("⚠️ Ви вже записані на цей матч.")
        else:
            print("DB Error:", e)
            await callback.answer("❌ Сталася помилка. Спробуйте пізніше.")


@router.callback_query(F.data.startswith("unregister_match:"))
async def unregister_from_match(callback: CallbackQuery, db: Database, state: FSMContext):
    match_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    query = """
            DELETE
            FROM registrations
            WHERE match_id = %s
              AND telegram_id = %s
            """
    await db.execute(query, (match_id, user_id))

    await callback.message.answer("❌Ви відмовилися від матчу. "
                                  "Напишіть причину, чому ви не прийдете і запропонуйте (якщо можливо) свій час. ")

    await state.set_state(GameStates.waiting_for_decline_reason)
    await state.update_data(match_id=match_id)

@router.message(GameStates.waiting_for_decline_reason)
async def process_decline_reason(message: Message, db: Database, state: FSMContext):
    reason = message.text.strip()
    data = await state.get_data()
    match_id = data.get("match_id")
    telegram_id = message.from_user.id
    username = message.from_user.username
    query_get_user = """
                     SELECT first_name, username FROM users WHERE telegram_id = %s
                     """
    user = await db.fetchone(query_get_user, (telegram_id,))
    if not user:
        raise ValueError("Користувача не знайдено в базі.")
    first_name, username = user
    
    query = """
            INSERT INTO registrations (match_id, telegram_id, first_name, username, message)
            VALUES (%s, %s, %s, %s, %s) AS new_reg
            ON DUPLICATE KEY UPDATE 
            message = new_reg.message, 
            registered_at = NOW()
            """
    await db.execute(query, (match_id, telegram_id, first_name, username, reason))
    await message.answer("👌 Дякую, повідомлення відправлене адміну!")
    await state.clear()



@router.callback_query(F.data.startswith("match_participants:"))
async def show_match_participants(callback: CallbackQuery, db: Database):
    match_id = int(callback.data.split(":")[1])

    query = """
            SELECT first_name, username, message
            FROM registrations
            WHERE match_id = %s
            """
    participants = await db.fetchall(query, (match_id,))

    if not participants:
        await callback.answer("😔 Ще ніхто не записався на цей матч.", show_alert=True)
        return

    text = f"👥 <b>Учасники матчу #{match_id}</b>\n\n"
    active_count = 0
    for idx, (first_name, username, message) in enumerate(participants, start=1):
        if message is not None:
            continue
        active_count += 1
        if first_name:
            first_name = first_name
        else:
            first_name = "-"
        if username:
            username = username
        else:
            username = "-"
        user_display = f"{first_name}, @{username}"
        text += f"{active_count}. {user_display}\n"

    if active_count == 0:
        text += "😔 Активних учасників поки немає."
    
    # Додаємо кнопку "Назад"
    from app.keyboards.inline import InlineKeyboardMarkup, InlineKeyboardButton
    back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_schedule:{match_id}")]
    ])

    await callback.message.edit_text(text, reply_markup=back_button)
    await callback.answer()



@router.message(F.text == "🔥 Наступний матч!")
async def show_next_game(message: Message, db: Database):
    query = """
            SELECT first_name, date, time, message
            FROM schedule
            WHERE date >= CURRENT_DATE
            ORDER BY date, time
                LIMIT 1
            """
    result = await db.fetchone(query)

    if not result:
        await message.answer(
            "📭 <b>Розклад поки що порожній</b>\n\n"
            "🔔 Ви отримаєте повідомлення, коли адмін додасть новий матч!\n\n"
            "⚽ Готуйтеся до гри!"
        )
        return

    first_name, date, time_, msg = result

    from datetime import datetime
    try:
        date_obj = datetime.strptime(str(date), "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d.%m.%Y")
        day_name = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"][date_obj.weekday()]
    except:
        formatted_date = str(date)
        day_name = ""

    text = "🎯 <b>НАСТУПНИЙ МАТЧ</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📅 <b>Дата:</b> {formatted_date} ({day_name})\n"
    text += f"🕐 <b>Час:</b> {time_}\n"
    text += f"👨‍💼 <b>Організатор:</b> {first_name}\n"
    text += f"📋 <b>Деталі:</b> {msg}\n"

    await message.answer(text)


@router.callback_query(F.data.startswith("back_to_schedule:"))
async def back_to_schedule(callback: CallbackQuery, db: Database):
    try:
        target_match_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка у форматі callback data.")
        return

    query = """
            SELECT first_name, date, time, message
            FROM schedule
            ORDER BY date, time \
            """
    result = await db.fetchall(query)

    if not result:
        await callback.message.edit_text(
            "📭 <b>Розклад поки що порожній</b>\n\n"
            "🔔 Ви отримаєте повідомлення, коли адмін додасть новий матч!\n\n"
            "⚽ Готуйтеся до гри!"
        )
        await callback.answer()
        return

    from datetime import datetime
    matches_by_date = {}
    for row in result:
        first_name, date, time_, msg = row
        date_key = str(date)
        matches_by_date.setdefault(date_key, []).append((first_name, date, time_, msg))

    text = "⚽ <b>🏆 РОЗКЛАД МАТЧІВ 🏆</b> ⚽\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    date_index = 0
    for date_key, matches in matches_by_date.items():
        date_index += 1
        if date_index == target_match_id:
            try:
                date_obj = datetime.strptime(date_key, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d.%m.%Y")
                day_name = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"][date_obj.weekday()]
            except:
                formatted_date = date_key
                day_name = ""

            text += f"📅 <b>{formatted_date}</b>"
            if day_name:
                text += f" ({day_name})"
            text += "\n"
            text += "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"

            match_number = 0
            for first_name, date, time_, msg in matches:
                match_number += 1
                text += f"🎯 <b>Матч #{match_number}</b>\n"
                text += f"🕐 <b>Час:</b> {time_}\n"
                text += f"👨‍💼 <b>Організатор:</b> {first_name}\n"
                text += f"📋 <b>Деталі:</b> {msg}\n"
                text += f"━━━━━━━━━━━━━━━━━━\n\n"
            break  # після того як знайшли потрібну дату — можна вийти з циклу

    text += "⚡ <i>Завжди будьте готові до гри!</i> ⚡\n"
    text += "🔥 <i>Футбол - це життя!</i> 🔥"

    await callback.message.edit_text(text)
    await callback.answer()



@router.message(F.text == "📋 Мої матчі")
async def my_registrations(message: Message, db: Database):
    query = """
            SELECT s.date, s.time, s.message
            FROM registrations r
                     JOIN schedule s ON s.id = r.match_id
            WHERE r.telegram_id = %s AND (r.message IS NULL OR r.message = '')
            ORDER BY s.date, s.time
            """
    matches = await db.fetchall(query, (message.from_user.id,))

    if not matches:
        await message.answer(
            "📭 <b>Ви ще не записалися на жоден матч</b>\n\n"
            "🔔 Перегляньте розклад та запишіться на майбутні ігри!\n\n"
            "⚽ Готуйтеся до гри!"
        )
        return

    from datetime import datetime
    
    text = "📋 <b>ВАШІ ЗАПЛАНОВАНІ МАТЧІ</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, (date, time_, schedule_msg) in enumerate(matches, 1):
        try:
            date_obj = datetime.strptime(str(date), "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            day_name = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"][date_obj.weekday()]
        except:
            formatted_date = str(date)
            day_name = ""
        
        # Перевіряємо повідомлення
        if schedule_msg is None:
            schedule_msg = "Без деталей"
        
        text += f"🎯 <b>МАТЧ #{i}</b>\n"
        text += f"📅 <b>Дата:</b> {formatted_date} ({day_name})\n"
        text += f"🕐 <b>Час:</b> {time_}\n"
        text += f"📋 <b>Деталі матчу:</b> {schedule_msg}\n\n"
    
    text += "⚡ <i>Побачимося на полі!</i> ⚡"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


    await message.answer(text)


# Обробник видалення матчу (тільки для адміна)
@router.callback_query(F.data.startswith("delete_match:"))
async def delete_match_callback(callback: CallbackQuery, db: Database):
    match_id = int(callback.data.split(":")[1])
    await db.execute("DELETE FROM schedule WHERE id = %s", (match_id,))
    await callback.message.edit_text("🗑️ Матч видалено адміністратором.")
    await callback.answer("Матч видалено!")
