from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from app.db.database import Database
from app.keyboards.inline import faq_main_menu
from app.db.models import add_user, save_feedback

from app.keyboards.inline import back_to_menu
from app.keyboards.reply import start_keyboard

from app.keyboards.reply import get_main_panel
from app.states.register import FeedbackStates

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

#FAQ LOGIC
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
async def faq_admin(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛠️ <b>Хочете щось запропонувати або повідомити про баг</b>\n\n"
        "Напиши напряму адміну: @cartuuz",
        reply_markup=back_to_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "faq_back")
async def faq_back(callback: CallbackQuery):
    keyboard = faq_main_menu()
    await callback.message.edit_text("❓ <b>Вибери розділ:</b>", reply_markup=keyboard)
    await callback.answer()

#ADMIN LOGIC
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
        await message.answer("✅ Дякуємо за ваш відгук!")
    except Exception as e:
        await message.answer("❌ Помилка під час збереження відгуку.")
        print(f"[FEEDBACK ERROR] {e}")

    await state.clear()
