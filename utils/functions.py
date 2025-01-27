from utils.database import insert_into_expences, select_from_expences, delete_from_expences



def insert_expence(telegram_id: int, category: str, amount: float) -> str:

    expence = {}
    expence["telegram_id"] = telegram_id
    expence["category"] = category
    expence["amount"] = amount

    try:

        insert_into_expences(expence)

        response = f"Записано!\nВитрата із категорії '{category}', на суму {float(amount)}грн."
    
    except Exception:

        response = "Помилка!\nНа жаль витрату не вдалося записати. Спробуй ще раз."
    
    return response


def delete_expence(telegram_id: int, category: str = None, amount: float = None,
                   start_datetime: str = None, end_datetime: str = None) -> str:
    
    filters = {}
    filters["telegram_id"] = telegram_id
    if category is not None: filters["category"] = category
    if amount is not None: filters["amount"] = amount
    if start_datetime is not None and end_datetime is not None: filters["created"] = (start_datetime, end_datetime)

    try:

        expences = select_from_expences(filters)

        expence = max(expences, key=lambda expence: expence["id"])

        category = expence["category"]
        amount = expence["amount"]
        created = expence["created"]

        delete_from_expences(expence)

        response = f"Видалено!\nВитрата із категорії '{category}', на суму {float(amount)}грн., дата/час: {created}."
    
    except Exception:

        response = "Помилка!\nНа жаль витрату не вдалося видалити. Спробуй ще раз."
    
    return response


def select_expences(telegram_id: int, category: str = None, amount: float = None,
                    start_datetime: str = None, end_datetime: str = None) -> str:
    
    filters = {}
    filters["telegram_id"] = telegram_id
    if category is not None: filters["category"] = category
    if amount is not None: filters["amount"] = amount
    if start_datetime is not None and end_datetime is not None: filters["created"] = (start_datetime, end_datetime)

    try:

        expences = []

        for expence in select_from_expences(filters):

            category = expence["category"]
            amount = expence["amount"]
            created = expence["created"]

            expences.append(f"- витрата із категорії '{category}', на суму {float(amount)}грн., дата/час: {created}.")
        
        expences = "\n".join(expences)

        if expences:

            response = f"Виконано!\nОсь твої витрати виходячи з наданих умов:\n{expences}"
        
        else:

            response = "Виконано!\nАле витрат виходячи з наданих умов не знайдено."
    
    except Exception:

        response = "Помилка!\nНа жаль витрати не вдалося вивантажити. Спробуй ще раз."
    
    return response


functions_register = {
    "insert_expence": insert_expence,
    "delete_expence": delete_expence,
    "select_expences": select_expences
}