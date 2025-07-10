from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Погоджуюся")],
    ],
    resize_keyboard=True
)

def get_main_panel(is_registered: bool, is_admin: bool = False) -> ReplyKeyboardMarkup:
    if not is_registered:
        buttons = [
            [KeyboardButton(text="Зареєструватися")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="📅 Розклад"), KeyboardButton(text="❓ FAQ")]
        ]
        
        # Додаємо кнопку адмін-панелі для адмінів
        if is_admin:
            buttons.append([KeyboardButton(text="🔐 Адмін-панель")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


