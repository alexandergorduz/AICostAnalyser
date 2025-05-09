import uuid
import base64
from io import BytesIO
from openai import OpenAI
from config import OPEN_AI_TOKEN, LLM_ID, AUDIO_LLM
from aiogram import Router, F
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from utils.assistant import text_assistant, image_assistant, audio_assistant



router = Router()

client = OpenAI(api_key=OPEN_AI_TOKEN)


@router.message(F.text)
async def message_text_handler(message: Message) -> None:

    response = text_assistant(message, client)

    if isinstance(response, str):

        await message.answer(response)
    
    elif isinstance(response, BytesIO):

        await message.answer_photo(BufferedInputFile(response.read(), filename=f"{uuid.uuid4().hex}.png"), caption="Ось статистика за вказаними параметрами.")


@router.message(F.photo)
async def message_image_handler(message: Message) -> None:

    photo = message.photo[-1]

    file = await message.bot.get_file(photo.file_id)

    file_path = file.file_path
    file_bytes = await message.bot.download_file(file_path)
    image_data = file_bytes.read()

    base64_str = base64.b64encode(image_data).decode('utf-8')

    response = client.chat.completions.create(
        model=LLM_ID,
        messages=[
            {
                "role": "system",
                "content": "Ти помічник в парсингу витрат із фотографій, твоя задача максимально точно розпарсити текст конкретних позицій/витрат із фото."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_str}"
                        }
                    }
                ]
            }
        ]
    )

    image_text = response.choices[0].message.content

    response = image_assistant(message, image_text, client)

    if isinstance(response, str):

        await message.answer(response)
    
    elif isinstance(response, BytesIO):

        await message.answer_photo(BufferedInputFile(response.read(), filename=f"{uuid.uuid4().hex}.png"), caption="Ось статистика за вказаними параметрами.")


@router.message(F.voice | F.audio)
async def handle_audio(message: Message):
    
    audio = message.voice if message.voice else message.audio

    file = await message.bot.get_file(audio.file_id)
    file_stream = await message.bot.download_file(file.file_path)
    file_stream.seek(0)

    ogg_file = ("audio.ogg", file_stream, "audio/ogg")

    response = client.audio.transcriptions.create(
        model=AUDIO_LLM,
        file=ogg_file
    )

    audio_text = response.text

    response = audio_assistant(message, audio_text, client)

    if isinstance(response, str):

        await message.answer(response)
    
    elif isinstance(response, BytesIO):

        await message.answer_photo(BufferedInputFile(response.read(), filename=f"{uuid.uuid4().hex}.png"), caption="Ось статистика за вказаними параметрами.")