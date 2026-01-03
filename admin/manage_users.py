import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_users(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Users",
        bg="#1e1e2f",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(filter_frame, text="Filter by Role:",
             bg="#1e1e2f", fg="white",
             font=("Segoe UI", 11, "bold")
             ).pack(side="left", padx=5)

    role_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Admin", "Manager", "Trainer", "Member"],
        state="readonly",
        width=18
    )
    role_filter.set("All")
    role_filter.pack(side="left", padx=5)

    tk.Label(filter_frame, text="Search by User ID:",
             bg="#1e1e2f", fg="white",
             font=("Segoe UI", 11, "bold")
             ).pack(side="left", padx=10)

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=5)

    # ================= FORM =================
    form_frame = tk.Frame(content, bg="#252540")
    form_frame.pack(fill="x", padx=30, pady=20)

    def form_label(text, r, c):
        tk.Label(
            form_frame,
            text=text,
            bg="#252540",
            fg="white",
            font=("Segoe UI", 10)
        ).grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def form_entry(r, c):
        e = tk.Entry(form_frame, width=28)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    # ---- Row 0
    form_label("User ID", 0, 0)
    user_id = form_entry(0, 1)

    form_label("Name", 0, 2)
    name = form_entry(0, 3)

    # ---- Row 1
    form_label("Email", 1, 0)
    email = form_entry(1, 1)

    form_label("Password", 1, 2)
    password = form_entry(1, 3)

    # ---- Row 2
    form_label("Contact", 2, 0)
    contact = form_entry(2, 1)

    form_label("Role", 2, 2)
    role = ttk.Combobox(
        form_frame,
        values=["Admin", "Manager", "Trainer", "Member"],
        state="readonly",
        width=25
    )
    role.grid(row=2, column=3, padx=10, pady=8)
    role.set("Member")

    # ---- Row 3
    form_label("Trainer ID", 3, 0)
    trainer_id = form_entry(3, 1)

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
            font=("Segoe UI", 10, "bold"),
            command=cmd
        ).pack(side="left", padx=6)

    # ================= TABLE =================
    table_frame = tk.Frame(content, bg="#2f2f4f")
    table_frame.pack(fill="both", expand=True, padx=30, pady=20)

    tree = ttk.Treeview(
        table_frame,
        columns=("id", "name", "email", "contact", "role", "trainer_id"),
        show="headings"
    )

    headings = [
        ("id", "User ID"),
        ("name", "Name"),
        ("email", "Email"),
        ("contact", "Contact"),
        ("role", "Role"),
        ("trainer_id", "Trainer ID")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=140, anchor="center")

    tree.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # ================= FUNCTIONS =================
    def clear_form():
        for e in [user_id, name, email, password, contact, trainer_id]:
            e.delete(0, tk.END)
        role.set("Member")

    def load_users_table():
        tree.delete(*tree.get_children())

        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT id, username, email, contact, role, trainer_id
            FROM users
        """
        conditions = []
        params = []

        if role_filter.get() != "All":
            conditions.append("role=%s")
            params.append(role_filter.get())

        if search_entry.get().strip():
            conditions.append("id LIKE %s")
            params.append(f"%{search_entry.get().strip()}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_user():
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users
                (username, email, password, contact, role, trainer_id)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    name.get(),
                    email.get(),
                    password.get(),
                    contact.get(),
                    role.get(),
                    trainer_id.get() if trainer_id.get() else None
                )
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User added successfully")
            clear_form()
            load_users_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_user():
        if not user_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE users SET
            username=%s,
            email=%s,
            password=%s,
            contact=%s,
            role=%s,
            trainer_id=%s
            WHERE id=%s
            """,
            (
                name.get(),
                email.get(),
                password.get(),
                contact.get(),
                role.get(),
                trainer_id.get() if trainer_id.get() else None,
                user_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "User updated successfully")
        load_users_table()

    def delete_user():
        if not user_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this user?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (user_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_users_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()

        user_id.insert(0, data[0])
        name.insert(0, data[1])
        email.insert(0, data[2])
        contact.insert(0, data[3])
        role.set(data[4])
        if data[5] is not None:
            trainer_id.insert(0, data[5])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add User", "#2196F3", add_user)
    action_btn("Update", "#FF9800", update_user)
    action_btn("Delete", "#F44336", delete_user)
    action_btn("Clear", "#607D8B", clear_form)

    role_filter.bind("<<ComboboxSelected>>", lambda e: load_users_table())
    search_entry.bind("<KeyRelease>", lambda e: load_users_table())

    load_users_table()
