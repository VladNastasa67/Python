from database import get_connection
from datetime import datetime


def add_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (name) VALUES (?)",
            (name,)
        )
        conn.commit()
    except Exception as e:
        print("Eroare categorie:", e)
    finally:
        conn.close()


def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    rows = cursor.fetchall()
    conn.close()
    return rows



def validate_expense(date, amount):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        if amount <= 0:
            return False
        return True
    except:
        return False


def add_expense(date, amount, category_id, note=""):
    if not validate_expense(date, amount):
        print("Date invalide!")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO expenses (date, amount, category_id, note)
        VALUES (?, ?, ?, ?)
        """,
        (date, amount, category_id, note)
    )
    conn.commit()
    conn.close()


def get_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.date, e.amount, c.name, e.note
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )
    conn.commit()
    conn.close()

def update_expense(expense_id, date, amount, category_id, note=""):
    if not validate_expense(date, amount):
        print("Date invalide!")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE expenses
        SET date = ?, amount = ?, category_id = ?, note = ?
        WHERE id = ?
        """,
        (date, amount, category_id, note, expense_id)
    )

    conn.commit()
    conn.close()
    return True

