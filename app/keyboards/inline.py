
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_to_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад до FAQ", callback_data="faq_back")]
        ]
    )

def faq_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Про бота", callback_data="faq_about")],
            [InlineKeyboardButton(text="📅 Матчі", callback_data="faq_matches")],
            [InlineKeyboardButton(text="🛠️ Зв'язок з адміном", callback_data="faq_admin")]
        ]
    )

def admin_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Управління користувачами", callback_data="admin_users")],
            [InlineKeyboardButton(text="📨 Зв'язок з користувачами", callback_data="admin_contacts")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Розсилка повідомлення", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="⚽ Запланувати новий матч", callback_data="admin_plan_game")],
            [InlineKeyboardButton(text="💬 Відгуки", callback_data="admin_feedbacks")]
        ]
    )

def admin_users_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Список користувачів", callback_data="admin_user_list")],
            [InlineKeyboardButton(text="🔍 Знайти користувача", callback_data="admin_user_search")],
            [InlineKeyboardButton(text="👑 Додати адміна", callback_data="admin_add_admin")],
            [InlineKeyboardButton(text="❌ Видалити адміна", callback_data="admin_remove_admin")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
        ]
    )

def admin_back():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад до адмін-панелі", callback_data="admin_back")]
        ]
    )

def user_action_menu(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👑 Зробити адміном", callback_data=f"admin_make_admin_{user_id}")],
            [InlineKeyboardButton(text="🚫 Заблокувати", callback_data=f"admin_ban_user_{user_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_user_list")]
        ]
    )

