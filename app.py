from database import init_db
from models import (
    add_category, get_categories,
    add_expense, get_expenses,
    update_expense
)

if __name__ == "__main__":
    init_db()

    print("Cheltuieli inițiale:")
    for e in get_expenses():
        print(e)

    # UPDATE: modificăm cheltuiala cu id=1
    update_expense(
        expense_id=1,
        date="2025-01-15",
        amount=150,
        category_id=1,
        note="Cumpărături actualizate"
    )

    print("\nDupă UPDATE:")
    for e in get_expenses():
        print(e)
