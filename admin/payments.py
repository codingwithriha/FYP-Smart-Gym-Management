import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
from datetime import date

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection  # Your database connection function


def load_manage_payments(content):
    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Payments",
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
        values=["All", "Paid", "Unpaid", "Pending", "Failed"],
        state="readonly",
        width=18
    )
    status_filter.set("All")
    status_filter.pack(side="left", padx=(0, 20))

    tk.Label(
        filter_frame,
        text="Search by Payment ID:",
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
    form_label("Payment ID", 0, 0)
    payment_id = form_entry(0, 1)

    form_label("Member ID", 0, 2)
    member_id = form_entry(0, 3)

    form_label("Amount", 1, 0)
    amount = form_entry(1, 1)

    form_label("Payment Date (YYYY-MM-DD)", 1, 2)
    payment_date = form_entry(1, 3)
    payment_date.insert(0, date.today().strftime("%Y-%m-%d"))

    form_label("Method", 2, 0)
    method = ttk.Combobox(
        form_frame,
        values=["Cash", "Credit Card", "Online"],
        state="readonly",
        width=25
    )
    method.grid(row=2, column=1, padx=10, pady=8)
    method.set("Cash")

    form_label("Discount", 2, 2)
    discount = form_entry(2, 3)

    form_label("Gym ID", 3, 0)
    gym_id = form_entry(3, 1)

    form_label("Loyalty Reward", 3, 2)
    loyalty = form_entry(3, 3)

    form_label("Status", 4, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Paid", "Unpaid", "Pending", "Failed"],
        state="readonly",
        width=25
    )
    status.grid(row=4, column=1, padx=10, pady=8)
    status.set("Paid")

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
        columns=("payment_id","member_id","amount","payment_date","method","discount","gym_id","loyalty","status"),
        show="headings"
    )

    headings = [
        ("payment_id","Payment ID"),
        ("member_id","Member ID"),
        ("amount","Amount"),
        ("payment_date","Payment Date"),
        ("method","Method"),
        ("discount","Discount"),
        ("gym_id","Gym ID"),
        ("loyalty","Loyalty Reward"),
        ("status","Status")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=120)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        payment_id.delete(0, tk.END)
        member_id.delete(0, tk.END)
        amount.delete(0, tk.END)
        payment_date.delete(0, tk.END)
        payment_date.insert(0, date.today().strftime("%Y-%m-%d"))
        method.set("Cash")
        discount.delete(0, tk.END)
        gym_id.delete(0, tk.END)
        loyalty.delete(0, tk.END)
        status.set("Paid")

    def load_payments_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT payment_id, member_id, amount, payment_date, method, discount, gym_id, loyalty, status FROM payments"
        params = []
        where = []

        if status_filter.get() != "All":
            where.append("status=%s")
            params.append(status_filter.get())
        if search_entry.get():
            where.append("payment_id LIKE %s")
            params.append(f"%{search_entry.get()}%")

        if where:
            query += " WHERE " + " AND ".join(where)

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    # ================= CRUD =================
    def add_payment():
        if not member_id.get() or not amount.get() or not payment_date.get():
            messagebox.showwarning("Required", "Please fill all required fields")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO payments (member_id, amount, payment_date, method, discount, gym_id, loyalty, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (member_id.get(), amount.get(), payment_date.get(), method.get(),
             discount.get() or 0, gym_id.get() or None, loyalty.get() or 0, status.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Payment added successfully")
        clear_form()
        load_payments_table()

    def update_payment():
        if not payment_id.get():
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE payments SET
            member_id=%s, amount=%s, payment_date=%s, method=%s,
            discount=%s, gym_id=%s, loyalty=%s, status=%s
            WHERE payment_id=%s
            """,
            (member_id.get(), amount.get(), payment_date.get(), method.get(),
             discount.get() or 0, gym_id.get() or None, loyalty.get() or 0, status.get(),
             payment_id.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Payment updated successfully")
        load_payments_table()

    def delete_payment():
        if not payment_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this payment record?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM payments WHERE payment_id=%s", (payment_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_payments_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        payment_id.insert(0, data[0])
        member_id.insert(0, data[1])
        amount.insert(0, data[2])
        payment_date.delete(0, tk.END)
        payment_date.insert(0, data[3])
        method.set(data[4])
        discount.delete(0, tk.END)
        discount.insert(0, data[5])
        gym_id.delete(0, tk.END)
        gym_id.insert(0, data[6])
        loyalty.delete(0, tk.END)
        loyalty.insert(0, data[7])
        status.set(data[8])

    tree.bind("<<TreeviewSelect>>", on_row_select)
    search_entry.bind("<KeyRelease>", lambda e: load_payments_table())
    status_filter.bind("<<ComboboxSelected>>", lambda e: load_payments_table())

    # ================= BUTTONS =================
    action_btn("Add Payment", "#2196F3", add_payment)
    action_btn("Update", "#FF9800", update_payment)
    action_btn("Delete", "#F44336", delete_payment)
    action_btn("Clear", "#607D8B", clear_form)

    load_payments_table()
