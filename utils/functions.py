from io import BytesIO
from typing import Any
import matplotlib.pyplot as plt
from utils.database import insert_into_expences, select_from_expences, delete_from_expences



def insert_expence(telegram_id: int, category: str, amount: float) -> str:

    expence = {}
    expence["telegram_id"] = telegram_id
    expence["category"] = category
    expence["amount"] = amount

    try:

        insert_into_expences(expence)

        formatted_amount = f"{float(amount):_.2f}".replace('_', ' ')

        response = (f"✅ <b>Записано!</b>\n\n"
                    f"Витрата із категорії '<b>{category}</b>',\n"
                    f"на суму <b>{int(float(formatted_amount))}</b> грн.")
    
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


def get_statistics(telegram_id: int, start_datetime: str, end_datetime: str) -> Any:

    filters = {}
    filters["telegram_id"] = telegram_id
    filters["created"] = (start_datetime, end_datetime)

    try:

        expences = select_from_expences(filters)

        if expences:

            category_totals = {}
            
            for expence in expences:

                category = expence["category"]
                amount = expence["amount"]

                if category not in category_totals:
                    
                    category_totals[category] = 0.0
                
                category_totals[category] += amount
            
            # Sort categories by amount for better visualization
            sorted_categories = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
            
            categories = [item[0] for item in sorted_categories]
            amounts = [item[1] for item in sorted_categories]
            total_amount = sum(amounts)

            # Use a more visually appealing color palette
            colors = plt.cm.Pastel2(range(len(categories)))

            plt.figure(figsize=(10, 7)) # Adjusted figure size
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%', 
                startangle=140, # Slightly rotated for better label positioning with many categories
                colors=colors,
                wedgeprops=dict(width=0.4, edgecolor='w'), # Donut chart style
                shadow=True,
                labeldistance=1.15 # Adjust radial distance of labels
            )

            # Improve text properties
            for text in texts:
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_color('black')
            
            plt.title(f"Розподіл витрат по категоріям\nЗагальна сума: {total_amount:_.2f} грн".replace('_', ' '), fontsize=14, pad=20)
            
            # Add a legend if there are many categories, or for better clarity
            if len(categories) > 5:
                 plt.legend(wedges, categories, title="Категорії", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.tight_layout(pad=1.5) # Adjusted padding
            response = BytesIO()
            plt.savefig(response, format="png", bbox_inches='tight') # Ensure the legend is saved if outside plot
            plt.close()
            response.seek(0)
        
        else:

            response = "Виконано!\nАле витрат виходячи з наданих умов не знайдено."
    
    except Exception:

        response = "Помилка!\nНа жаль статистику не вдалося вивантажити. Спробуй ще раз."
    
    return response


functions_register = {
    "insert_expence": insert_expence,
    "delete_expence": delete_expence,
    "select_expences": select_expences,
    "get_statistics": get_statistics
}