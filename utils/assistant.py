import json
from io import BytesIO
from datetime import datetime
from openai import OpenAI
from config import LLM_ID
from aiogram.types import Message
from utils.database import select_from_categories
from utils.functions import functions_register



messages_buffer = {}


def text_assistant(message: Message, client: OpenAI) -> str:

    telegram_id = message.from_user.id
    text = message.text
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    categories = [category["category"] for category in select_from_categories()]

    if telegram_id not in messages_buffer:

        messages_buffer[telegram_id] = []
    
    messages_buffer[telegram_id].append(
        {
            "role": "user",
            "content": text
        }
    )

    functions = [
        {
            "type": "function",
            "function": {
                "name": "insert_expence",
                "description": "Функція використовується для запису витрати.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених.",
                            "enum": categories
                        },
                        "amount": {
                            "type": "number",
                            "description": "Сума витрати."
                        }
                    },
                    "required": ["category", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_expence",
                "description": "Функція використовується для пошуку та видалення витрати.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених",
                            "enum": categories
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "select_expences",
                "description": "Функція використовується для вивантаження витрат.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених.",
                            "enum": categories
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
            }
        },
        {
            "type": "function",
            "function": {
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
        }
    ]

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"Ти асистент для фіксації та аналізу витрат користувача. Твоя задача отримувати інформацію щодо витрат, розпізнавати до якої категорії відноситься витрата та виконувати відповідний функціонал. Ти відповідаєш тільки на запити пов'язані із витратами клієнта. Валюта витрат виключно гривня (грн). Краще перепитай якщо не впевнений в складних витратах. Поточна дата/час: {now}."
            }
        ] + messages_buffer[telegram_id],
        model=LLM_ID,
        tools=functions
    )

    ai_message = response.choices[0].message
    messages_buffer[telegram_id].append(ai_message)

    if ai_message.content:

        return ai_message.content
    
    if ai_message.tool_calls:

        results = []

        for tool_call in ai_message.tool_calls:

            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_args["telegram_id"] = telegram_id

            result = functions_register[tool_name](**tool_args)

            if isinstance(result, BytesIO):

                messages_buffer[telegram_id].append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": "Виведена статистика за вказаними параметрами."
                    }
                )

                return result

            results.append(result)

            messages_buffer[telegram_id].append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
            )
        
        return "\n\n".join(results)


def image_assistant(message: Message, image_text: str, client: OpenAI) -> str:

    telegram_id = message.from_user.id
    text = image_text
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    categories = [category["category"] for category in select_from_categories()]

    if telegram_id not in messages_buffer:

        messages_buffer[telegram_id] = []
    
    messages_buffer[telegram_id].append(
        {
            "role": "user",
            "content": text
        }
    )

    functions = [
        {
            "type": "function",
            "function": {
                "name": "insert_expence",
                "description": "Функція використовується для запису витрати.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених.",
                            "enum": categories
                        },
                        "amount": {
                            "type": "number",
                            "description": "Сума витрати."
                        }
                    },
                    "required": ["category", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_expence",
                "description": "Функція використовується для пошуку та видалення витрати.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених",
                            "enum": categories
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "select_expences",
                "description": "Функція використовується для вивантаження витрат.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених.",
                            "enum": categories
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
            }
        },
        {
            "type": "function",
            "function": {
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
        }
    ]

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"Ти асистент для фіксації та аналізу витрат користувача. Твоя задача отримувати інформацію щодо витрат, розпізнавати до якої категорії відноситься витрата та виконувати відповідний функціонал. Ти відповідаєш тільки на запити пов'язані із витратами клієнта. Валюта витрат виключно гривня (грн). Виведи отримані позиції для підтвердження користувачем. Поточна дата/час: {now}."
            }
        ] + messages_buffer[telegram_id],
        model=LLM_ID,
        tools=functions
    )

    ai_message = response.choices[0].message
    messages_buffer[telegram_id].append(ai_message)

    if ai_message.content:

        return ai_message.content
    
    if ai_message.tool_calls:

        results = []

        for tool_call in ai_message.tool_calls:

            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_args["telegram_id"] = telegram_id

            result = functions_register[tool_name](**tool_args)

            if isinstance(result, BytesIO):

                messages_buffer[telegram_id].append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": "Виведена статистика за вказаними параметрами."
                    }
                )

                return result

            results.append(result)

            messages_buffer[telegram_id].append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
            )
        
        return "\n\n".join(results)


def audio_assistant(message: Message, audio_text: str, client: OpenAI) -> str:

    telegram_id = message.from_user.id
    text = audio_text
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    categories = [category["category"] for category in select_from_categories()]

    if telegram_id not in messages_buffer:

        messages_buffer[telegram_id] = []
    
    messages_buffer[telegram_id].append(
        {
            "role": "user",
            "content": text
        }
    )

    functions = [
        {
            "type": "function",
            "function": {
                "name": "insert_expence",
                "description": "Функція використовується для запису витрати.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених.",
                            "enum": categories
                        },
                        "amount": {
                            "type": "number",
                            "description": "Сума витрати."
                        }
                    },
                    "required": ["category", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_expence",
                "description": "Функція використовується для пошуку та видалення витрати.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених",
                            "enum": categories
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "select_expences",
                "description": "Функція використовується для вивантаження витрат.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": f"Категорія витрати, яка відповідає одній із дозволених.",
                            "enum": categories
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
            }
        },
        {
            "type": "function",
            "function": {
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
        }
    ]

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"Ти асистент для фіксації та аналізу витрат користувача. Твоя задача отримувати інформацію щодо витрат, розпізнавати до якої категорії відноситься витрата та виконувати відповідний функціонал. Ти відповідаєш тільки на запити пов'язані із витратами клієнта. Валюта витрат виключно гривня (грн). Виведи отримані позиції для підтвердження користувачем. Поточна дата/час: {now}."
            }
        ] + messages_buffer[telegram_id],
        model=LLM_ID,
        tools=functions
    )

    ai_message = response.choices[0].message
    messages_buffer[telegram_id].append(ai_message)

    if ai_message.content:

        return ai_message.content
    
    if ai_message.tool_calls:

        results = []

        for tool_call in ai_message.tool_calls:

            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_args["telegram_id"] = telegram_id

            result = functions_register[tool_name](**tool_args)

            if isinstance(result, BytesIO):

                messages_buffer[telegram_id].append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": "Виведена статистика за вказаними параметрами."
                    }
                )

                return result

            results.append(result)

            messages_buffer[telegram_id].append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
            )
        
        return "\n\n".join(results)