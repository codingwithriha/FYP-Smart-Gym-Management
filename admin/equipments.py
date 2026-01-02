import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
from datetime import datetime

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection

def load_manage_equipment(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Equipment",
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
        values=["All", "Active", "Inactive", "Under Maintenance"],
        state="readonly",
        width=20
    )
    status_filter.set("All")
    status_filter.pack(side="left", padx=(0, 20))

    tk.Label(
        filter_frame,
        text="Search by Name:",
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
    form_label("Equipment ID", 0, 0)
    equipment_id = form_entry(0, 1)

    form_label("Name", 0, 2)
    name = form_entry(0, 3)

    form_label("Category", 1, 0)
    category = ttk.Combobox(
        form_frame,
        values=["Cardio", "Strength", "Free Weights", "Machines"],
        state="readonly",
        width=25
    )
    category.grid(row=1, column=1, padx=10, pady=8)
    category.set("Cardio")

    form_label("Quantity", 1, 2)
    quantity = form_entry(1, 3)

    form_label("Status", 2, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Active", "Inactive", "Under Maintenance"],
        state="readonly",
        width=25
    )
    status.grid(row=2, column=1, padx=10, pady=8)
    status.set("Active")

    form_label("Purchase Date (YYYY-MM-DD)", 2, 2)
    purchase_date = form_entry(2, 3)

    form_label("Last Maintenance (YYYY-MM-DD)", 3, 0)
    last_maintenance = form_entry(3, 1)

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
        columns=("equipment_id", "name", "category", "quantity", "status", "purchase_date", "last_maintenance"),
        show="headings"
    )

    headings = [
        ("equipment_id", "Equipment ID"),
        ("name", "Name"),
        ("category", "Category"),
        ("quantity", "Quantity"),
        ("status", "Status"),
        ("purchase_date", "Purchase Date"),
        ("last_maintenance", "Last Maintenance")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        equipment_id.delete(0, tk.END)
        name.delete(0, tk.END)
        category.set("Cardio")
        quantity.delete(0, tk.END)
        status.set("Active")
        purchase_date.delete(0, tk.END)
        last_maintenance.delete(0, tk.END)

    def load_equipment_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT equipment_id, name, category, quantity, status, purchase_date, last_maintenance
            FROM equipment
        """
        params = []
        where = []

        if status_filter.get() != "All":
            where.append("status=%s")
            params.append(status_filter.get())

        if search_entry.get():
            where.append("name LIKE %s")
            params.append(f"%{search_entry.get()}%")

        if where:
            query += " WHERE " + " AND ".join(where)

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    # ================= CRUD =================
    def add_equipment():
        if not name.get() or not quantity.get():
            messagebox.showwarning("Required", "Please fill all required fields")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO equipment (name, category, quantity, status, purchase_date, last_maintenance)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name.get(), category.get(), quantity.get(), status.get(), purchase_date.get(), last_maintenance.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Equipment added successfully")
        clear_form()
        load_equipment_table()

    def update_equipment():
        if not equipment_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE equipment SET
            name=%s, category=%s, quantity=%s, status=%s, purchase_date=%s, last_maintenance=%s
            WHERE equipment_id=%s
            """,
            (name.get(), category.get(), quantity.get(), status.get(), purchase_date.get(), last_maintenance.get(), equipment_id.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Equipment updated successfully")
        load_equipment_table()

    def delete_equipment():
        if not equipment_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this equipment?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM equipment WHERE equipment_id=%s", (equipment_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_equipment_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        equipment_id.insert(0, data[0])
        name.insert(0, data[1])
        category.set(data[2])
        quantity.insert(0, data[3])
        status.set(data[4])
        purchase_date.insert(0, data[5])
        last_maintenance.insert(0, data[6])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= LIVE SEARCH & FILTER =================
    search_entry.bind("<KeyRelease>", lambda e: load_equipment_table())
    status_filter.bind("<<ComboboxSelected>>", lambda e: load_equipment_table())

    # ================= BUTTONS =================
    action_btn("Add Equipment", "#2196F3", add_equipment)
    action_btn("Update", "#FF9800", update_equipment)
    action_btn("Delete", "#F44336", delete_equipment)
    action_btn("Clear", "#607D8B", clear_form)

    load_equipment_table()
