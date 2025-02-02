from io import BytesIO
import uuid
from aiogram import Router, F
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from utils.assistant import text_assistant



router = Router()


@router.message(F.text)
async def message_text_handler(message: Message) -> None:

    response = text_assistant(message)

    if isinstance(response, str):

        await message.answer(response)
    
    elif isinstance(response, BytesIO):

        await message.answer_photo(BufferedInputFile(response.read(), filename=f"{uuid.uuid4().hex}.png"), caption="Ось статистика за вказаними параметрами.")