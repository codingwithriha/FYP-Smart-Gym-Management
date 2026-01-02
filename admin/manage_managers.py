import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection

def load_manage_managers(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Managers",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    # 🔹 Filter Label + Combobox
    tk.Label(
        filter_frame,
        text="Filter by Department:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    department_filter = ttk.Combobox(
        filter_frame,
        values=[
            "All",
            "Operations",
            "Membership Management",
            "Fitness & Training",
            "Sales & Marketing",
            "Customer Services",
            "Human Resources",
            "Finance & Billing",
            "Equipment Nutrition & Diet Plan",
            "IT & System Support"
        ],
        state="readonly",
        width=28
    )
    department_filter.set("All")
    department_filter.pack(side="left", padx=(0, 15))

    # 🔹 Search Label + Entry
    tk.Label(
        filter_frame,
        text="Search by Manager ID:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

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
        command=lambda: load_managers_table()
    ).pack(side="left")

    # 🔹 Live search & filter
    search_entry.bind("<KeyRelease>", lambda e: load_managers_table())
    department_filter.bind("<<ComboboxSelected>>", lambda e: load_managers_table())

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

    # ================= FORM FIELDS =================
    form_label("Manager ID", 0, 0)
    manager_id = form_entry(0, 1)

    form_label("Qualification", 0, 2)
    qualification = form_entry(0, 3)

    form_label("Department", 1, 0)
    department = ttk.Combobox(
        form_frame,
        values=[
            "Operations",
            "Membership Management",
            "Fitness & Training",
            "Sales & Marketing",
            "Customer Services",
            "Human Resources",
            "Finance & Billing",
            "Equipment Nutrition & Diet Plan",
            "IT & System Support"
        ],
        state="readonly",
        width=25
    )
    department.grid(row=1, column=1, padx=10, pady=8)

    form_label("Hire Date (YYYY-MM-DD)", 1, 2)
    hire_date = form_entry(1, 3)

    form_label("Emergency Contact", 2, 0)
    emergency_contact = form_entry(2, 1)

    form_label("Gym ID", 2, 2)
    gym_id = form_entry(2, 3)

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
            "id", "qualification", "department",
            "hire_date", "contact", "gym"
        ),
        show="headings"
    )

    headings = [
        ("id", "Manager ID"),
        ("qualification", "Qualification"),
        ("department", "Department"),
        ("hire_date", "Hire Date"),
        ("contact", "Emergency Contact"),
        ("gym", "Gym ID")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        manager_id.delete(0, tk.END)
        qualification.delete(0, tk.END)
        department.set("")
        hire_date.delete(0, tk.END)
        emergency_contact.delete(0, tk.END)
        gym_id.delete(0, tk.END)

    def load_managers_table():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT manager_id, qualification, department,
                          hire_date, emergency_contact, gym_id
                   FROM managers"""
        conditions = []
        params = []

        # 🔹 FILTER (Department)
        if department_filter.get() != "All":
            conditions.append("department=%s")
            params.append(department_filter.get())

        # 🔹 SEARCH (Manager ID)
        search_text = search_entry.get().strip()
        if search_text:
            conditions.append("manager_id LIKE %s")
            params.append(f"%{search_text}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY manager_id DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_manager():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO managers
               (qualification, department, hire_date, emergency_contact, gym_id)
               VALUES (%s,%s,%s,%s,%s)""",
            (
                qualification.get(),
                department.get(),
                hire_date.get(),
                emergency_contact.get(),
                gym_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Manager added successfully")
        clear_form()
        load_managers_table()

    def update_manager():
        if not manager_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE managers SET
               qualification=%s,
               department=%s,
               hire_date=%s,
               emergency_contact=%s,
               gym_id=%s
               WHERE manager_id=%s""",
            (
                qualification.get(),
                department.get(),
                hire_date.get(),
                emergency_contact.get(),
                gym_id.get(),
                manager_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Manager updated successfully")
        load_managers_table()

    def delete_manager():
        if not manager_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this manager?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM managers WHERE manager_id=%s", (manager_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_managers_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        manager_id.insert(0, data[0])
        qualification.insert(0, data[1])
        department.set(data[2])
        hire_date.insert(0, data[3])
        emergency_contact.insert(0, data[4])
        gym_id.insert(0, data[5])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add Manager", "#2196F3", add_manager)
    action_btn("Update", "#FF9800", update_manager)
    action_btn("Delete", "#F44336", delete_manager)
    action_btn("Clear", "#607D8B", clear_form)

    # 🔹 Load initial data
    load_managers_table()
