from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.database import (
    insert_into_users, 
    select_from_users,
    get_expense_count_by_telegram_id,
    get_expense_sum_by_telegram_id
)

router = Router()

@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:

    user = {
        "telegram_id": message.from_user.id,
        "first_name": message.from_user.first_name or "Unknown",
        "last_name": message.from_user.last_name or "Unknown",
        "username": message.from_user.username or "Unknown"
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Аналітика за 30 днів", switch_inline_query_current_chat="Покажи мою аналітику за останні 30 днів.")]
    ])

    if user["telegram_id"] in [user["telegram_id"] for user in select_from_users()]:

        expense_count = get_expense_count_by_telegram_id(user["telegram_id"])
        expense_sum = get_expense_sum_by_telegram_id(user["telegram_id"])
        
        formatted_sum = f"{expense_sum:_.2f}".replace('_', ' ')

        await message.answer(f"Привіт, <b>{user["first_name"]}</b>! 👋\n\n"
                             f"Я твій персональний фінансовий помічник, готовий допомогти тобі відстежувати витрати. 🤖\n\n"
                             f"📊 Наразі ти зафіксував <b>{expense_count}</b> позицій\n"
                             f"💰 На загальну суму <b>{formatted_sum}</b> грн.\n\n"
                             f"Готовий фіксувати твої нові витрати!",
                             reply_markup=keyboard,
                             parse_mode="HTML")
    
    else:

        insert_into_users(user)

        await message.answer("Привіт!\bЯ бот який допомагає фіксувати твої витрати та проводити їх аналітику.", reply_markup=keyboard)

@router.message(F.text.lower() == "покажи мою аналітику за останні 30 днів.")
async def text_show_30_day_analytics_handler(message: Message) -> None:
    await message.answer("Незабаром тут буде аналітика твоїх витрат за останні 30 днів.")

@router.message(Command("last_30_days_analytics"))
async def command_last_30_days_analytics_handler(message: Message) -> None:
    await message.answer("Незабаром тут буде аналітика твоїх витрат за останні 30 днів.")