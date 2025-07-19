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


async def send_to_admins(bot, db: Database, text: str):
    """
    Надсилає повідомлення всім адмінам
    """
    admins = await get_admins(db)

    for admin in admins:
        admin_id = admin[0]
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            print(f"[ERROR] Не вдалося надіслати адміну {admin_id}: {e}")


async def send_match_notifications(bot, db: Database):
    """
    Перевіряє матчі і надсилає повідомлення користувачам згідно з налаштуваннями
    """
    from datetime import datetime, timedelta
    import pytz
    
    # Використовуємо стандартні налаштування (30, 60, 120 хвилин)
    notification_times = [30, 60, 120]
    
    kyiv_tz = pytz.timezone('Europe/Kiev')
    current_time = datetime.now(kyiv_tz)
    
    print(f"🔄 Перевіряю матчі о {current_time.strftime('%H:%M:%S')}")
    
    total_sent = 0
    
    for minutes_before in notification_times:
        # Розраховуємо час матчу, для якого треба надіслати повідомлення
        target_match_time = current_time + timedelta(minutes=minutes_before)
        
        # Шукаємо матчі, які починаються через вказану кількість хвилин (±2 хвилини)
        start_window = target_match_time - timedelta(minutes=2)
        end_window = target_match_time + timedelta(minutes=2)
        
        match_query = """
                SELECT s.id, s.date, s.time, s.message, s.first_name
                FROM schedule s
                WHERE (s.date + s.time)::timestamp BETWEEN $1 AND $2
                AND s.date >= CURRENT_DATE
                ORDER BY s.date, s.time
                """
        
        matches = await db.fetchall(match_query, (
            start_window.strftime("%Y-%m-%d %H:%M:%S"),
            end_window.strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        for match_id, date, time_str, match_message, organizer in matches:
            print(f"🎯 Знайдено матч: {date} {time_str} (за {minutes_before} хв)")
            
            # Отримуємо список учасників
            participants_query = """
                    SELECT DISTINCT r.telegram_id, u.first_name
                    FROM registrations r
                    JOIN users u ON u.telegram_id = r.telegram_id
                    WHERE r.match_id = $1 
                    AND (r.message IS NULL OR r.message = '')
                    """
            
            participants = await db.fetchall(participants_query, (match_id,))
            
            if not participants:
                print(f"   ℹ️ Немає учасників для матчу {match_id}")
                continue
            
            # Формуємо повідомлення
            try:
                date_obj = datetime.strptime(str(date), "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d.%m.%Y")
                day_name = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"][date_obj.weekday()]
            except:
                formatted_date = str(date)
                day_name = ""
            
            notification_text = f"🔔 <b>НАГАДУВАННЯ ПРО МАТЧ!</b>\n\n"
            notification_text += f"⚡ Матч почнеться через {minutes_before} хвилин!\n\n"
            notification_text += f"📅 <b>Дата:</b> {formatted_date} ({day_name})\n"
            notification_text += f"🕐 <b>Час:</b> {time_str}\n"
            notification_text += f"👨‍💼 <b>Організатор:</b> {organizer}\n"
            if match_message:
                notification_text += f"📋 <b>Деталі:</b> {match_message}\n"
            notification_text += f"\n⚽ Готуйтеся до гри!"
            
            # Надсилаємо повідомлення всім учасникам
            sent_count = 0
            failed_count = 0
            
            for telegram_id, first_name in participants:
                try:
                    await bot.send_message(telegram_id, notification_text)
                    print(f"   ✅ Повідомлення надіслано: {first_name} ({telegram_id})")
                    sent_count += 1
                except Exception as e:
                    print(f"   ❌ Помилка для {first_name} ({telegram_id}): {e}")
                    failed_count += 1
            
            total_sent += sent_count
            print(f"   📊 Результат: {sent_count} надіслано, {failed_count} помилок")
    
    if total_sent > 0:
        print(f"🎯 Загалом надіслано {total_sent} повідомлень")
    else:
        print("ℹ️ Жодного повідомлення не надіслано")


