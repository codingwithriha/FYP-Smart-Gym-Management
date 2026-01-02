import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_salaries(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Salaries",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(
        filter_frame,
        text="Filter by Status:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    status_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Active", "Inactive"],
        state="readonly",
        width=18
    )
    status_filter.set("All")
    status_filter.pack(side="left", padx=(0, 20))

    tk.Label(
        filter_frame,
        text="Search by Salary ID:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=(0, 10))

    # ================= FORM =================
    form_frame = tk.Frame(content, bg="#252540")
    form_frame.pack(fill="x", padx=30, pady=20)

    def form_label(text, r, c):
        tk.Label(
            form_frame,
            text=text,
            bg="#252540",
            fg="white",
            font=("Arial", 11)
        ).grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def form_entry(r, c):
        e = tk.Entry(form_frame, width=28)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    # ================= FORM FIELDS =================
    form_label("Salary ID", 0, 0)
    salary_id = form_entry(0, 1)

    form_label("User ID", 0, 2)
    user_id = form_entry(0, 3)

    form_label("Amount", 1, 0)
    amount = form_entry(1, 1)

    form_label("Pay Date (YYYY-MM-DD)", 1, 2)
    pay_date = form_entry(1, 3)

    form_label("Status", 2, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Active", "Inactive"],
        state="readonly",
        width=25
    )
    status.grid(row=2, column=1, padx=10, pady=8)
    status.set("Active")

    # ================= BUTTONS =================
    btn_frame = tk.Frame(content, bg="#1e1e2f")
    btn_frame.pack(anchor="w", padx=30, pady=15)

    def action_btn(text, color, cmd):
        tk.Button(
            btn_frame,
            text=text,
            bg=color,
            fg="white",
            bd=0,
            padx=18,
            pady=8,
            font=("Arial", 10, "bold"),
            command=cmd
        ).pack(side="left", padx=5)

    # ================= TABLE =================
    table_frame = tk.Frame(content, bg="#2f2f4f")
    table_frame.pack(fill="both", expand=True, padx=30, pady=20)

    tree = ttk.Treeview(
        table_frame,
        columns=("salary_id", "user_id", "amount", "pay_date", "status"),
        show="headings"
    )

    headings = [
        ("salary_id", "Salary ID"),
        ("user_id", "User ID"),
        ("amount", "Amount"),
        ("pay_date", "Pay Date"),
        ("status", "Status")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=160)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        salary_id.delete(0, tk.END)
        user_id.delete(0, tk.END)
        amount.delete(0, tk.END)
        pay_date.delete(0, tk.END)
        status.set("Active")

    def load_salaries_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT salary_id, user_id, amount, pay_date, status
            FROM salaries
        """
        params = []
        where = []

        if status_filter.get() != "All":
            where.append("status=%s")
            params.append(status_filter.get())

        if search_entry.get():
            where.append("salary_id LIKE %s")
            params.append(f"%{search_entry.get()}%")

        if where:
            query += " WHERE " + " AND ".join(where)

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    # ================= CRUD =================
    def add_salary():
        if not user_id.get() or not amount.get() or not pay_date.get():
            messagebox.showwarning("Required", "Please fill all required fields")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO salaries (user_id, amount, pay_date, status)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id.get(), amount.get(), pay_date.get(), status.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Salary added successfully")
        clear_form()
        load_salaries_table()

    def update_salary():
        if not salary_id.get():
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE salaries SET
            user_id=%s,
            amount=%s,
            pay_date=%s,
            status=%s
            WHERE salary_id=%s
            """,
            (
                user_id.get(),
                amount.get(),
                pay_date.get(),
                status.get(),
                salary_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Salary updated successfully")
        load_salaries_table()

    def delete_salary():
        if not salary_id.get():
            return

        if not messagebox.askyesno("Confirm", "Delete this salary record?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM salaries WHERE salary_id=%s",
            (salary_id.get(),)
        )
        conn.commit()
        conn.close()
        clear_form()
        load_salaries_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return

        data = tree.item(selected)["values"]
        clear_form()
        salary_id.insert(0, data[0])
        user_id.insert(0, data[1])
        amount.insert(0, data[2])
        pay_date.insert(0, data[3])
        status.set(data[4])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= LIVE SEARCH & FILTER =================
    search_entry.bind("<KeyRelease>", lambda e: load_salaries_table())
    status_filter.bind("<<ComboboxSelected>>", lambda e: load_salaries_table())

    # ================= BUTTONS =================
    action_btn("Add Salary", "#2196F3", add_salary)
    action_btn("Update", "#FF9800", update_salary)
    action_btn("Delete", "#F44336", delete_salary)
    action_btn("Clear", "#607D8B", clear_form)

    load_salaries_table()
