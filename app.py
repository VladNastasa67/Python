from gui import ExpenseApp
import tkinter as tk
from database import init_db

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
