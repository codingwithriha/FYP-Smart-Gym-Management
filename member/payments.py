import tkinter as tk
from tkinter import ttk
from database_db import get_connection

def load_payments_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Payments",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(10, 20))

    # ---------------- TREEVIEW + SCROLLBAR FRAME ----------------
    tree_frame = tk.Frame(content, bg="#1f1b2e")
    tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ---------------- TREEVIEW ----------------
    columns = ("amount", "payment_date", "method", "discount", "reward", "status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    # Column headings
    tree.heading("amount", text="Amount")
    tree.heading("payment_date", text="Date")
    tree.heading("method", text="Method")
    tree.heading("discount", text="Discount")
    tree.heading("reward", text="Reward")
    tree.heading("status", text="Status")

    # Column widths
    tree.column("amount", width=100, anchor="center")
    tree.column("payment_date", width=120, anchor="center")
    tree.column("method", width=120, anchor="center")
    tree.column("discount", width=100, anchor="center")
    tree.column("reward", width=100, anchor="center")
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
            SELECT amount, payment_date, method, discount, loyalty, status
            FROM payments
            WHERE member_id = %s
            ORDER BY payment_date DESC
        """
        cursor.execute(query, (member_id,))
        payments = cursor.fetchall()
        conn.close()

        # ---------------- INSERT DATA INTO TREEVIEW ----------------
        for payment in payments:
            tree.insert("", "end", values=payment)

    except Exception as e:
        tk.Label(
            content,
            text=f"Error fetching payments: {str(e)}",
            bg="#1f1b2e",
            fg="red",
            font=("Segoe UI", 12)
        ).pack(pady=20)
