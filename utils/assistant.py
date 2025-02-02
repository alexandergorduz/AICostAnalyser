import json
from datetime import datetime, timedelta
from openai import OpenAI
from config import OPEN_AI_TOKEN, LLM_ID
from aiogram.types import Message
from utils.database import select_from_categories
from utils.functions import functions_register



client = OpenAI(api_key=OPEN_AI_TOKEN)


messages_buffer = {}


def text_assistant(message: Message) -> str:

    telegram_id = message.from_user.id
    text = message.text
    now = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    categories = ", ".join([category["category"] for category in select_from_categories()])

    if telegram_id not in messages_buffer:

        messages_buffer[telegram_id] = [
            {
                "role": "system",
                "content": f"Ти асистент для фіксації та аналізу витрат користувача. Твоя задача отримувати інформацію щодо витрат, розпізнавати до якої категорії відноситься витрата та виконувати відповідний функціонал. Ти відповідаєш тільки на запити пов'язані із витратами клієнта. Валюта витрат виключно гривня (грн). Поточна дата/час: {now}."
            }
        ]
    
    messages_buffer[telegram_id].append(
        {
            "role": "user",
            "content": text
        }
    )

    functions = [
        {
            "name": "insert_expence",
            "description": "Функція використовується для запису витрати.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": f"Категорія витрати, яка відповідає одній із дозволених: {categories}."
                    },
                    "amount": {
                        "type": "number",
                        "description": "Сума витрати."
                    }
                },
                "required": ["category", "amount"]
            }
        },
        {
            "name": "delete_expence",
            "description": "Функція використовується для пошуку та видалення витрати.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": f"Категорія витрати, яка відповідає одній із дозволених: {categories}."
                    },
                    "amount": {
                        "type": "number",
                        "description": "Сума витрати."
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": "Дата початку пошуку у форматі 'YYYY-MM-DD HH:MM:SS'."
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": "Дата кінця пошуку у форматі 'YYYY-MM-DD HH:MM:SS'."
                    }
                }
            }
        },
        {
            "name": "select_expences",
            "description": "Функція використовується для вивантаження витрат.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": f"Категорія витрати, яка відповідає одній із дозволених: {categories}."
                    },
                    "amount": {
                        "type": "number",
                        "description": "Сума витрати."
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": "Дата початку пошуку у форматі 'YYYY-MM-DD HH:MM:SS'."
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": "Дата кінця пошуку у форматі 'YYYY-MM-DD HH:MM:SS'."
                    }
                }
            }
        },
        {
            "name": "get_statistics",
            "description": "Функція використовується для формування статистики по витратам і генерації картинки зі статистикою.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_datetime": {
                        "type": "string",
                        "description": "Дата початку пошуку у форматі 'YYYY-MM-DD HH:MM:SS'."
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": "Дата кінця пошуку у форматі 'YYYY-MM-DD HH:MM:SS'."
                    }
                },
                "required": ["start_datetime", "end_datetime"]
            }
        }
    ]

    response = client.chat.completions.create(
        messages=messages_buffer[telegram_id],
        model=LLM_ID,
        function_call="auto",
        functions=functions,
        temperature=0.1
    )

    function_call = response.choices[0].message.function_call

    if function_call:

        function_name = function_call.name
        function_arguments = json.loads(function_call.arguments)
        function_arguments["telegram_id"] = telegram_id

        response = functions_register[function_name](**function_arguments)

        del messages_buffer[telegram_id]
    
    else:

        response = response.choices[0].message.content

        messages_buffer[telegram_id].append(
            {
                "role": "assistant",
                "content": response
            }
        )
    
    return response