import tkinter as tk
from tkinter import ttk, messagebox
from models import add_expense, get_expenses, get_categories, delete_expense, update_expense, add_category
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import csv
from tkinter import filedialog


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x600")

        self.categories = get_categories()
        self.selected_id = None
        self.month_var = tk.StringVar()
        self.filter_category_var = tk.StringVar()
        self.new_category_var = tk.StringVar()




        self.build_form()
        self.build_table()
        self.build_reports()
        self.load_expenses()

    def build_form(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=10)

        tk.Label(frame, text="Date").grid(row=0, column=0)
        tk.Label(frame, text="Amount").grid(row=0, column=2)
        tk.Label(frame, text="Category").grid(row=1, column=0)
        tk.Label(frame, text="Note").grid(row=1, column=2)

        self.date_entry = tk.Entry(frame)
        self.amount_entry = tk.Entry(frame)

        self.category_var = tk.StringVar()
        self.category_box = ttk.Combobox(
            frame,
            textvariable=self.category_var,
            values=[c[1] for c in self.categories],
            state="readonly"
        )

        self.note_entry = tk.Entry(frame)

        self.date_entry.grid(row=0, column=1, padx=5)
        self.amount_entry.grid(row=0, column=3, padx=5)
        self.category_box.grid(row=1, column=1, padx=5)
        self.note_entry.grid(row=1, column=3, padx=5)

        tk.Button(frame, text="Add", command=self.add_expense).grid(row=2, column=0, pady=10)
        tk.Button(frame, text="Update", command=self.update_selected).grid(row=2, column=1, pady=10)
        tk.Button(frame, text="Delete", command=self.delete_selected).grid(row=2, column=2, pady=10)
        
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill="x", padx=10)

        tk.Label(filter_frame, text="Month").pack(side="left")
        self.month_box = ttk.Combobox(filter_frame, textvariable=self.month_var, state="readonly")
        self.month_box.pack(side="left", padx=5)
        self.month_box.bind("<<ComboboxSelected>>", self.load_expenses)

        tk.Label(filter_frame, text="Category").pack(side="left", padx=(20, 0))
        self.filter_category_box = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_category_var,
            values=["All"] + [c[1] for c in self.categories],
             state="readonly"
        )
        self.filter_category_box.pack(side="left", padx=5)
        self.filter_category_box.bind("<<ComboboxSelected>>", self.load_expenses)

        category_frame = tk.Frame(self.root)
        category_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(category_frame, text="New category").pack(side="left")
        self.new_category_entry = tk.Entry(category_frame, textvariable=self.new_category_var)
        self.new_category_entry.pack(side="left", padx=5)

        tk.Button(category_frame, text="Add category", command=self.add_category).pack(side="left")
        tk.Button(filter_frame, text="Export CSV", command=self.export_csv).pack(side="right")



    def build_table(self):
       frame = tk.Frame(self.root)
       frame.pack(fill="both", expand=True, padx=10)

       columns = ("id", "date", "amount", "category", "note")
       self.tree = ttk.Treeview(frame, columns=columns, show="headings")

       self.tree.heading("id", text="Id")
       self.tree.heading("date", text="Date")
       self.tree.heading("amount", text="Amount")
       self.tree.heading("category", text="Category")
       self.tree.heading("note", text="Note")

       self.tree.column("id", width=60, anchor="center", stretch=False)
       self.tree.column("date", width=120, anchor="center", stretch=False)
       self.tree.column("amount", width=120, anchor="center", stretch=False)
       self.tree.column("category", width=150, anchor="center", stretch=False)
       self.tree.column("note", width=800, anchor="center", stretch=False)

       self.tree.bind("<<TreeviewSelect>>", self.on_select)


       y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
       x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)

       self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

       self.tree.grid(row=0, column=0, sticky="nsew")
       y_scroll.grid(row=0, column=1, sticky="ns")
       x_scroll.grid(row=1, column=0, sticky="ew")
       

       frame.grid_rowconfigure(0, weight=1)
       frame.grid_columnconfigure(0, weight=1)

       self.total_label = tk.Label(self.root, text="Total: 0")
       self.total_label.pack(pady=5)


    def build_reports(self):
        frame=tk.Frame(self.root)
        frame.pack(fill="both", expand=False, padx=10, pady=10)

        self.fig=Figure(figsize=(8,3))
        self.ax_pie = self.fig.add_subplot(121)
        self.ax_bar = self.fig.add_subplot(122)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_chart_click)


    def load_expenses(self, event=None):
        for row in self.tree.get_children():
           self.tree.delete(row)

        expenses = get_expenses()

        months = sorted({e[1][:7] for e in expenses})
        self.month_box["values"] = ["All"] + months
        

        selected_month = self.month_var.get()
        selected_category = self.filter_category_var.get()
        total = 0
        per_category = defaultdict(float)

        for e in expenses:
            if selected_month and selected_month != "All":
                if not e[1].startswith(selected_month):
                    continue

            if selected_category and selected_category != "All":
                if e[3] != selected_category:
                    continue
            self.tree.insert("", "end", values=e)
            total += e[2]
            per_category[e[3]] += e[2]

        self.total_label.config(text=f"Total: {total}")
        self.selected_id = None
    
        self.update_charts(per_category)

    def on_chart_click(self, event):
        if event.inaxes == self.ax_pie:
            for wedge, label in zip(self.ax_pie.patches, self.ax_pie.texts):
                if wedge.contains_point((event.x, event.y)):
                    self.highlight_category(label.get_text())
                    return

        if event.inaxes == self.ax_bar:
            for bar, label in zip(self.ax_bar.patches, self.ax_bar.get_xticklabels()):
               if bar.contains(event)[0]:
                    self.highlight_category(label.get_text())
                    return

    def highlight_category(self, category):
        for row in self.tree.get_children():
            values = self.tree.item(row)["values"]
            if values[3] == category:
               self.tree.selection_add(row)
            else:
               self.tree.selection_remove(row)


    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        self.selected_id = values[0]

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[1])

        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, values[2])

        self.category_var.set(values[3])

        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, values[4])

    def add_expense(self):
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category_name = self.category_var.get()
        note = self.note_entry.get()

        if not date or not amount or not category_name:
            messagebox.showerror("Error", "Missing fields")
            return

        try:
            amount = float(amount)
        except:
            messagebox.showerror("Error", "Invalid amount")
            return

        category_id = next(c[0] for c in self.categories if c[1] == category_name)

        add_expense(date, amount, category_id, note)
        self.load_expenses()
    
    def add_category(self):
        name = self.new_category_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Category name required")
            return

        add_category(name)
        self.categories = get_categories()

        self.category_box["values"] = [c[1] for c in self.categories]
        self.filter_category_box["values"] = ["All"] + [c[1] for c in self.categories]

        self.new_category_var.set("")


    def update_selected(self):
        if self.selected_id is None:
            messagebox.showerror("Error", "No selection")
            return

        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category_name = self.category_var.get()
        note = self.note_entry.get()

        try:
            amount = float(amount)
        except:
            messagebox.showerror("Error", "Invalid amount")
            return

        category_id = next(c[0] for c in self.categories if c[1] == category_name)

        update_expense(self.selected_id, date, amount, category_id, note)
        self.load_expenses()

    def delete_selected(self):
        if self.selected_id is None:
            messagebox.showerror("Error", "No selection")
            return

        delete_expense(self.selected_id)
        self.load_expenses()

    def update_charts(self, per_category):
       self.ax_pie.clear()
       self.ax_bar.clear()

       if not per_category:
           self.canvas.draw()
           return

       labels = list(per_category.keys())
       values = list(per_category.values())

       self.ax_pie.pie(values, labels=labels, autopct="%1.1f%%")
       self.ax_pie.set_title("Share by category")

       self.ax_bar.bar(labels, values)
       self.ax_bar.set_title("Amount by category")
       self.ax_bar.set_ylabel("Amount")

       self.fig.tight_layout()
       self.canvas.draw()

    def export_csv(self):
        rows = []
        for item in self.tree.get_children():
           rows.append(self.tree.item(item)["values"])

        if not rows:
           messagebox.showerror("Error", "No data to export")
           return

        month = self.month_var.get()
        if not month or month == "All":
           month = "all"

        file_path = filedialog.asksaveasfilename(
           defaultextension=".csv",
           filetypes=[("CSV files", "*.csv")],
           initialfile=f"expenses_{month}.csv"
        )

        if not file_path:
           return

        try:
           with open(file_path, "w", newline="", encoding="utf-8") as f:
               writer = csv.writer(f)
               writer.writerow(["Id", "Date", "Amount", "Category", "Note"])
               for r in rows:
                   writer.writerow(r)

           messagebox.showinfo("Success", "Export completed successfully")

        except Exception:
            messagebox.showerror("Error", "Failed to export CSV")

