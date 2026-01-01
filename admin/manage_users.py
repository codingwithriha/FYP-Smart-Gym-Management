import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

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
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    role_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Admin", "Manager", "Trainer", "Member"],
        state="readonly",
        width=18
    )
    role_filter.set("All")
    role_filter.pack(side="left", padx=(0, 10))

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=(0, 10))

    tk.Button(
        filter_frame,
        text="Search",
        bg="#4CAF50",
        fg="white",
        bd=0,
        padx=20,
        pady=6,
        command=lambda: load_users_table()
    ).pack(side="left")

    # ================= FORM =================
    form_frame = tk.Frame(content, bg="#252540")
    form_frame.pack(fill="x", padx=30, pady=20)

    def form_label(text, r, c):
        tk.Label(
            form_frame,
            text=text,
            bg="#252540",
            fg="white"
        ).grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def form_entry(r, c):
        e = tk.Entry(form_frame, width=28)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    form_label("User ID", 0, 0)
    user_id = form_entry(0, 1)

    form_label("Name", 0, 2)
    name = form_entry(0, 3)

    form_label("Email", 1, 0)
    email = form_entry(1, 1)

    form_label("Password", 1, 2)
    password = form_entry(1, 3)

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
        columns=("id", "name", "email", "contact", "role"),
        show="headings"
    )

    for col in ("id", "name", "email", "contact", "role"):
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        user_id.delete(0, tk.END)
        name.delete(0, tk.END)
        email.delete(0, tk.END)
        password.delete(0, tk.END)
        contact.delete(0, tk.END)
        role.set("Member")

    def load_users_table():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()

        query = "SELECT id, username, email, contact, role FROM users"
        params = []

        if role_filter.get() != "All":
            query += " WHERE role=%s"
            params.append(role_filter.get())

        if search_entry.get():
            query += " AND username LIKE %s" if "WHERE" in query else " WHERE name LIKE %s"
            params.append(f"%{search_entry.get()}%")

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
                "INSERT INTO users (username,email,password,contact,role) VALUES (%s,%s,%s,%s,%s)",
                (name.get(), email.get(), password.get(), contact.get(), role.get())
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
            """UPDATE users SET username=%s,email=%s,password=%s,contact=%s,role=%s WHERE id=%s""",
            (name.get(), email.get(), password.get(), contact.get(), role.get(), user_id.get())
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

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add User", "#2196F3", add_user)
    action_btn("Update", "#FF9800", update_user)
    action_btn("Delete", "#F44336", delete_user)
    action_btn("Clear", "#607D8B", clear_form)

    load_users_table()
