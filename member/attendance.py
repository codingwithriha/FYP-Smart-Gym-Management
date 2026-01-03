import tkinter as tk
from tkinter import ttk
from database_db import get_connection

def load_attendance_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Attendance",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(10, 20))

    # ---------------- TREEVIEW + SCROLLBAR FRAME ----------------
    tree_frame = tk.Frame(content, bg="#1f1b2e")
    tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ---------------- TREEVIEW ----------------
    columns = ("date", "check_in", "check_out", "role")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    # Column headings
    tree.heading("date", text="Date")
    tree.heading("check_in", text="Check In")
    tree.heading("check_out", text="Check Out")
    tree.heading("role", text="Role")

    # Column widths
    tree.column("date", width=120, anchor="center")
    tree.column("check_in", width=100, anchor="center")
    tree.column("check_out", width=100, anchor="center")
    tree.column("role", width=100, anchor="center")

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
            SELECT date, check_in, check_out, role
            FROM attendance
            WHERE user_id = %s
            ORDER BY date DESC
        """
        cursor.execute(query, (member_id,))  # member_id = user_id
        attendance_records = cursor.fetchall()
        conn.close()

        # Insert data into Treeview
        for record in attendance_records:
            tree.insert("", "end", values=record)

    except Exception as e:
        tk.Label(
            content,
            text=f"Error fetching attendance: {str(e)}",
            bg="#1f1b2e",
            fg="red",
            font=("Segoe UI", 12)
        ).pack(pady=20)
