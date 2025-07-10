from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Погоджуюся")],
    ],
    resize_keyboard=True
)

def get_main_panel(is_registered: bool) -> ReplyKeyboardMarkup:
    if not is_registered:
        buttons = [
            [KeyboardButton(text="Зареєструватися")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="📅 Розклад"), KeyboardButton(text="❓ FAQ")]
        ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


