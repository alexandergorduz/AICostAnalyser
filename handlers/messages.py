from aiogram import Router, F
from aiogram.types import Message
from utils.assistant import text_assistant



router = Router()


@router.message(F.text)
async def message_text_handler(message: Message) -> None:

    await message.answer(text_assistant(message))