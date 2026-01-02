import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_announcements(content):
    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Announcements",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= SEARCH BAR =================
    search_frame = tk.Frame(content, bg="#1e1e2f")
    search_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(
        search_frame,
        text="Search by Title:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    search_entry = tk.Entry(search_frame, width=50)
    search_entry.pack(side="left", padx=(0, 10))

    # ================= FORM =================
    form_frame = tk.Frame(content, bg="#252540")
    form_frame.pack(fill="x", padx=30, pady=20)

    # Helper Functions
    def form_label(text, r, c):
        tk.Label(
            form_frame,
            text=text,
            bg="#252540",
            fg="white",
            font=("Arial", 11)
        ).grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def form_entry(r, c, width=25):
        e = tk.Entry(form_frame, width=width)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    # ================= FORM FIELDS (Side-by-side) =================
    # Row 0
    form_label("Announcement ID", 0, 0)
    announcement_id = form_entry(0, 1)

    form_label("Created At", 0, 2)
    created_at = form_entry(0, 3)

    # Row 1
    form_label("Title", 1, 0)
    title = form_entry(1, 1)

    form_label("Message", 1, 2)
    message = tk.Text(form_frame, width=30, height=6)
    message.grid(row=1, column=3, padx=10, pady=8)

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
        columns=("announcement_id", "title", "message", "created_at"),
        show="headings"
    )

    headings = [
        ("announcement_id", "Announcement ID"),
        ("title", "Title"),
        ("message", "Message"),
        ("created_at", "Created At")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=180 if col != "message" else 300)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        announcement_id.delete(0, tk.END)
        created_at.delete(0, tk.END)
        title.delete(0, tk.END)
        message.delete("1.0", tk.END)

    def load_announcements_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = "SELECT announcement_id, title, message, created_at FROM announcements"
        params = []
        if search_entry.get():
            query += " WHERE title LIKE %s"
            params.append(f"%{search_entry.get()}%")

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    # ================= CRUD =================
    def add_announcement():
        if not title.get() or not message.get("1.0", tk.END).strip():
            messagebox.showwarning("Required", "Please fill all required fields")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO announcements (announcement_id, title, message, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (
                announcement_id.get() if announcement_id.get() else None,
                title.get(),
                message.get("1.0", tk.END).strip(),
                created_at.get() if created_at.get() else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Announcement added successfully")
        clear_form()
        load_announcements_table()

    def update_announcement():
        if not announcement_id.get():
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE announcements SET
            title=%s,
            message=%s,
            created_at=%s
            WHERE announcement_id=%s
            """,
            (title.get(), message.get("1.0", tk.END).strip(), created_at.get(), announcement_id.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Announcement updated successfully")
        load_announcements_table()

    def delete_announcement():
        if not announcement_id.get():
            return

        if not messagebox.askyesno("Confirm", "Delete this announcement?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM announcements WHERE announcement_id=%s",
            (announcement_id.get(),)
        )
        conn.commit()
        conn.close()
        clear_form()
        load_announcements_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return

        data = tree.item(selected)["values"]
        clear_form()
        announcement_id.insert(0, data[0])
        title.insert(0, data[1])
        message.insert("1.0", data[2])
        created_at.insert(0, data[3])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= LIVE SEARCH =================
    search_entry.bind("<KeyRelease>", lambda e: load_announcements_table())

    # ================= BUTTONS =================
    action_btn("Add", "#2196F3", add_announcement)
    action_btn("Update", "#FF9800", update_announcement)
    action_btn("Delete", "#F44336", delete_announcement)
    action_btn("Clear", "#607D8B", clear_form)

    load_announcements_table()
