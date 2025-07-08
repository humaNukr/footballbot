from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Start")],
    ],
    resize_keyboard=True
)

main_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зареєструватися")],
        [KeyboardButton(text="FAQ")]
    ],
    resize_keyboard=True
)
