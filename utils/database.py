import sqlite3
from config import DATABASE_PATH
from typing import List, Dict, Tuple, Any

def initialize_database() -> None:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT NOT NULL,
            created TIMESTAMP DEFAULT (DATETIME('now')))
        """
    )

    connection.commit()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            created TIMESTAMP DEFAULT (DATETIME('now')))
        """
    )

    connection.commit()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS expences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            created TIMESTAMP DEFAULT (DATETIME('now')))
        """
    )

    connection.commit()

    connection.close()


def insert_into_users(user: Dict[str, Any]) -> None:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            telegram_id,
            first_name,
            last_name,
            username)
        VALUES (
            ?,
            ?,
            ?,
            ?)
        """,
        (
            user["telegram_id"],
            user["first_name"],
            user["last_name"],
            user["username"]
        )
    )

    connection.commit()

    connection.close()


def select_from_users(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            telegram_id,
            first_name,
            last_name,
            username,
            created
        FROM
            users
        """
    
    parameters = []

    if filters:

        conditions = []

        for field, value in filters.items():

            if isinstance(value, Tuple) and len(value) == 2:

                parameters.extend(value)
                conditions.append(f"{field} BETWEEN ? AND ?")
            
            else:

                parameters.append(value)
                conditions.append(f"{field} = ?")
        
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created"

    cursor.execute(query, parameters)

    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    connection.close()

    users = [dict(zip(columns, row)) for row in rows]

    return users


def delete_from_users(filters: Dict[str, Any]) -> None:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = """
        DELETE FROM
            users
        """
    
    parameters = []
    conditions = []

    for field, value in filters.items():

        parameters.append(value)
        conditions.append(f"{field} = ?")
    
    query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, parameters)

    connection.commit()

    connection.close()


def insert_into_categories(category: Dict[str, Any]) -> None:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO categories (
            category)
        VALUES (
            ?)
        """,
        (
            category["category"]
        )
    )

    connection.commit()

    connection.close()


def select_from_categories(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            category,
            created
        FROM
            categories
        """
    
    parameters = []

    if filters:

        conditions = []

        for field, value in filters.items():

            if isinstance(value, Tuple) and len(value) == 2:

                parameters.extend(value)
                conditions.append(f"{field} BETWEEN ? AND ?")
            
            else:

                parameters.append(value)
                conditions.append(f"{field} = ?")
        
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created"

    cursor.execute(query, parameters)

    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    connection.close()

    categories = [dict(zip(columns, row)) for row in rows]

    return categories


def delete_from_categories(filters: Dict[str, Any]) -> None:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = """
        DELETE FROM
            categories
        """
    
    parameters = []
    conditions = []

    for field, value in filters.items():

        parameters.append(value)
        conditions.append(f"{field} = ?")
    
    query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, parameters)

    connection.commit()

    connection.close()


def insert_into_expences(expence: Dict[str, Any]) -> None:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO expences (
            telegram_id,
            category,
            amount)
        VALUES (
            ?,
            ?,
            ?)
        """,
        (
            expence["telegram_id"],
            expence["category"],
            expence["amount"]
        )
    )

    connection.commit()

    connection.close()


def select_from_expences(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            telegram_id,
            category,
            amount,
            created
        FROM
            expences
        """
    
    parameters = []

    if filters:

        conditions = []

        for field, value in filters.items():

            if isinstance(value, Tuple) and len(value) == 2:

                parameters.extend(value)
                conditions.append(f"{field} BETWEEN ? AND ?")
            
            else:

                parameters.append(value)
                conditions.append(f"{field} = ?")
        
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created"

    cursor.execute(query, parameters)

    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    connection.close()

    expences = [dict(zip(columns, row)) for row in rows]

    return expences


def delete_from_expences(filters: Dict[str, Any]) -> None:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    query = """
        DELETE FROM
            expences
        """
    
    parameters = []
    conditions = []

    for field, value in filters.items():

        parameters.append(value)
        conditions.append(f"{field} = ?")
    
    query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, parameters)

    connection.commit()

    connection.close()


def get_expense_count_by_telegram_id(telegram_id: int) -> int:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*)
        FROM
            expences
        WHERE
            telegram_id = ?
        """,
        (telegram_id,)
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


def get_expense_sum_by_telegram_id(telegram_id: int) -> float:

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            SUM(amount)
        FROM
            expences
        WHERE
            telegram_id = ?
        """,
        (telegram_id,)
    )

    total_sum = cursor.fetchone()[0]

    connection.close()

    # Handle case where there are no expenses and SUM(amount) returns None
    return total_sum if total_sum is not None else 0.0