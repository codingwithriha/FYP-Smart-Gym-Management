import tkinter as tk
from tkinter import ttk
from database_db import get_connection

def load_announcements_page(content):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Announcements",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(10, 20))

    # ---------------- TREEVIEW + SCROLLBAR FRAME ----------------
    tree_frame = tk.Frame(content, bg="#1f1b2e")
    tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ---------------- TREEVIEW ----------------
    columns = ("title", "message", "created_at")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    # Column headings
    tree.heading("title", text="Title")
    tree.heading("message", text="Message")
    tree.heading("created_at", text="Date")

    # Column widths
    tree.column("title", width=200, anchor="center")
    tree.column("message", width=400, anchor="w")
    tree.column("created_at", width=120, anchor="center")

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
            SELECT title, message, created_at
            FROM announcements
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        announcements = cursor.fetchall()
        conn.close()

        # Insert data into Treeview
        for ann in announcements:
            tree.insert("", "end", values=ann)

    except Exception as e:
        tk.Label(
            content,
            text=f"Error fetching announcements: {str(e)}",
            bg="#1f1b2e",
            fg="red",
            font=("Segoe UI", 12)
        ).pack(pady=20)
