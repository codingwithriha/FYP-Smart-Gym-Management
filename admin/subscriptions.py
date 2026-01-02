import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_subscriptions(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Subscriptions",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(
        filter_frame,
        text="Filter by Plan Name:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    plan_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Basic Fitness", "Premium Fitness", "Personal Training", "Yoga Plan", "Nutrition Plan"],
        state="readonly",
        width=20
    )
    plan_filter.set("All")
    plan_filter.pack(side="left", padx=(0, 15))

    tk.Label(
        filter_frame,
        text="Search by Subscription ID:",
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
        tk.Label(form_frame, text=text, bg="#252540", fg="white")\
            .grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def form_entry(r, c):
        e = tk.Entry(form_frame, width=28)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    # ================= FORM FIELDS =================
    form_label("Subscription ID", 0, 0)
    subscription_id = form_entry(0, 1)

    form_label("Member ID", 0, 2)
    member_id = form_entry(0, 3)

    form_label("Plan Name", 1, 0)
    plan_name = ttk.Combobox(
        form_frame,
        values=[
            "Basic Fitness",
            "Premium Fitness",
            "Personal Training",
            "Yoga Plan",
            "Nutrition Plan"
        ],
        state="readonly",
        width=25
    )
    plan_name.grid(row=1, column=1, padx=10, pady=8)
    plan_name.set("Basic Fitness")

    form_label("Start Date (YYYY-MM-DD)", 1, 2)
    start_date = form_entry(1, 3)

    form_label("End Date (YYYY-MM-DD)", 2, 0)
    end_date = form_entry(2, 1)

    form_label("Amount Paid", 2, 2)
    amount_paid = form_entry(2, 3)

    form_label("Total Amount", 3, 0)
    total_amount = form_entry(3, 1)

    form_label("Status", 3, 2)
    status = ttk.Combobox(
        form_frame,
        values=["Active", "Expired", "Cancelled", "Pending"],
        state="readonly",
        width=25
    )
    status.grid(row=3, column=3, padx=10, pady=8)
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
            command=cmd
        ).pack(side="left", padx=5)

    # ================= TABLE =================
    table_frame = tk.Frame(content, bg="#2f2f4f")
    table_frame.pack(fill="both", expand=True, padx=30, pady=20)

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "subscription_id", "member_id", "plan_name",
            "start_date", "end_date", "amount_paid",
            "total_amount", "status"
        ),
        show="headings"
    )

    headings = [
        ("subscription_id", "Subscription ID"),
        ("member_id", "Member ID"),
        ("plan_name", "Plan Name"),
        ("start_date", "Start Date"),
        ("end_date", "End Date"),
        ("amount_paid", "Amount Paid"),
        ("total_amount", "Total Amount"),
        ("status", "Status")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=140)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        for e in [
            subscription_id, member_id, start_date,
            end_date, amount_paid, total_amount
        ]:
            e.delete(0, tk.END)
        plan_name.set("Basic Fitness")
        status.set("Active")

    def load_subscriptions_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT subscription_id, member_id, plan_name,
                   start_date, end_date, amount_paid,
                   total_amount, status
                   FROM subscriptions"""
        params = []
        where = []

        if plan_filter.get() != "All":
            where.append("plan_name=%s")
            params.append(plan_filter.get())

        if search_entry.get():
            where.append("subscription_id LIKE %s")
            params.append(f"%{search_entry.get()}%")

        if where:
            query += " WHERE " + " AND ".join(where)

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    # ================= CRUD =================
    def add_subscription():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO subscriptions
               (member_id, plan_name, start_date, end_date,
                amount_paid, total_amount, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                member_id.get(), plan_name.get(), start_date.get(),
                end_date.get(), amount_paid.get(),
                total_amount.get(), status.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Subscription added successfully")
        clear_form()
        load_subscriptions_table()

    def update_subscription():
        if not subscription_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE subscriptions SET
               member_id=%s, plan_name=%s, start_date=%s,
               end_date=%s, amount_paid=%s,
               total_amount=%s, status=%s
               WHERE subscription_id=%s""",
            (
                member_id.get(), plan_name.get(), start_date.get(),
                end_date.get(), amount_paid.get(),
                total_amount.get(), status.get(),
                subscription_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Subscription updated successfully")
        load_subscriptions_table()

    def delete_subscription():
        if not subscription_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this subscription?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM subscriptions WHERE subscription_id=%s", (subscription_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_subscriptions_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        subscription_id.insert(0, data[0])
        member_id.insert(0, data[1])
        plan_name.set(data[2])
        start_date.insert(0, data[3])
        end_date.insert(0, data[4])
        amount_paid.insert(0, data[5])
        total_amount.insert(0, data[6])
        status.set(data[7])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= LIVE SEARCH & FILTER =================
    search_entry.bind("<KeyRelease>", lambda e: load_subscriptions_table())
    plan_filter.bind("<<ComboboxSelected>>", lambda e: load_subscriptions_table())

    # ================= BUTTONS =================
    action_btn("Add Subscription", "#2196F3", add_subscription)
    action_btn("Update", "#FF9800", update_subscription)
    action_btn("Delete", "#F44336", delete_subscription)
    action_btn("Clear", "#607D8B", clear_form)

    load_subscriptions_table()
