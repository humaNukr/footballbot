from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from app.db.models import add_user

from app.keyboards.inline import back_to_menu
from app.keyboards.reply import start_keyboard

from app.keyboards.reply import get_main_panel

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Підтвердіть, що ви погоджуєтеся з політикою конфіденційності ⚽",
        reply_markup=start_keyboard
    )

@router.message(F.text == "🚀 Погоджуюся")
async def process_start_button(message: Message, is_registered: bool):
    await message.answer(
        "Виберіть одну з опцій:",
        reply_markup=get_main_panel(is_registered)
    )

#FAQ LOGIC
@router.message(F.text == "❓ FAQ")
async def show_faq_menu(message: Message):
    await message.answer(
        "Це розділи найчастіших питань ❗")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Про бота", callback_data="faq_about")],
            [InlineKeyboardButton(text="📅 Матчі", callback_data="faq_matches")],
            [InlineKeyboardButton(text="🛠️ Зв'язок з адміном", callback_data="faq_admin")]
        ]
    )
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
async def faq_admin(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛠️ <b>Хочете щось запропонувати або повідомити про баг</b>\n\n"
        "Напиши напряму адміну: @cartuuz",
        reply_markup=back_to_menu()
    )
    await callback.answer()




@router.callback_query(F.data == "faq_back")
async def faq_back(callback: CallbackQuery):
    await show_faq_menu(callback.message)
    await callback.answer()