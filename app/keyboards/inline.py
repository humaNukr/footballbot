from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def back_to_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад до FAQ", callback_data="faq_back")]
        ]
    )