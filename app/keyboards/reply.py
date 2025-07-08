from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Погоджуюся")],
    ],
    resize_keyboard=True
)

def get_main_panel(is_registered: bool) -> ReplyKeyboardMarkup:

    buttons = [
        [KeyboardButton(text="📅 Розклад"), KeyboardButton(text="❓ FAQ")]
    ]
    if not is_registered:
        buttons.remove([KeyboardButton(text="📅 Розклад"), KeyboardButton(text="❓ FAQ")])
        buttons.append([KeyboardButton(text="Зареєструватися")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


