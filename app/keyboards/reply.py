from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Погоджуюся")],
    ],
    resize_keyboard=True
)

main_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зареєструватися")],
        [KeyboardButton(text="❓ FAQ")]
    ],
    resize_keyboard=True
)
