import tkinter as tk
from tkinter import ttk
from database_db import get_connection

def load_subscription_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="My Subscription",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(10, 20))

    # ---------------- TREEVIEW + SCROLLBAR FRAME ----------------
    tree_frame = tk.Frame(content, bg="#1f1b2e")
    tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ---------------- TREEVIEW ----------------
    columns = ("plan_name", "start_date", "end_date", "paid", "total", "status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    # Column headings
    tree.heading("plan_name", text="Plan Name")
    tree.heading("start_date", text="Start Date")
    tree.heading("end_date", text="End Date")
    tree.heading("paid", text="Paid")
    tree.heading("total", text="Total")
    tree.heading("status", text="Status")

    # Column widths
    tree.column("plan_name", width=150, anchor="center")
    tree.column("start_date", width=100, anchor="center")
    tree.column("end_date", width=100, anchor="center")
    tree.column("paid", width=80, anchor="center")
    tree.column("total", width=80, anchor="center")
    tree.column("status", width=100, anchor="center")

    # ---------------- SCROLLBAR ----------------
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    # Pack Treeview and Scrollbar side by side
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="left", fill="y")

    # ---------------- FETCH DATA FROM DB ----------------
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT plan_name, start_date, end_date, amount_paid, total_amount, status
            FROM subscriptions
            WHERE member_id = %s
            ORDER BY start_date DESC
        """
        cursor.execute(query, (member_id,))
        subscriptions = cursor.fetchall()
        conn.close()

        # Insert data
        for sub in subscriptions:
            tree.insert("", "end", values=sub)

    except Exception as e:
        tk.Label(
            content,
            text=f"Error fetching subscriptions: {str(e)}",
            bg="#1f1b2e",
            fg="red",
            font=("Segoe UI", 12)
        ).pack(pady=20)
