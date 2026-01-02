import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection

def load_manage_gym_branches(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Gym Branches",
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
        text="Filter by City:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    city_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Islamabad", "Lahore", "Karachi"],
        state="readonly",
        width=20
    )
    city_filter.set("All")
    city_filter.pack(side="left", padx=(0, 15))

    # 🔹 Search Label + Entry
    tk.Label(
        filter_frame,
        text="Search by Branch Name:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=(0, 10))

    # tk.Button(
    #     filter_frame,
    #     text="Search",
    #     bg="#4CAF50",
    #     fg="white",
    #     bd=0,
    #     padx=20,
    #     pady=6,
    #     command=lambda: load_branches_table()
    # ).pack(side="left")

    # 🔹 Live search & filter
    search_entry.bind("<KeyRelease>", lambda e: load_branches_table())
    city_filter.bind("<<ComboboxSelected>>", lambda e: load_branches_table())

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
    form_label("Gym ID", 0, 0)
    branch_id = form_entry(0, 1)

    form_label("Branch Name", 0, 2)
    branch_name = form_entry(0, 3)

    form_label("City", 1, 0)
    city = ttk.Combobox(
        form_frame,
        values=["Islamabad", "Lahore", "Karachi"],
        state="readonly",
        width=25
    )
    city.grid(row=1, column=1, padx=10, pady=8)

    form_label("Area", 1, 2)
    area = ttk.Combobox(
        form_frame,
        values=[
            # Islamabad
            "F-6", "F-7", "F-8", "G-9", "G-10", "I-8", "Blue Area",
            # Lahore
            "DHA Phase 5", "Gulberg", "Johar Town", "Model Town", "Bahria Town",
            # Karachi
            "DHA", "Clifton", "Gulshan-e-Iqbal", "PECHS", "North Nazimabad"
        ],
        state="readonly",
        width=25
    )
    area.grid(row=1, column=3, padx=10, pady=8)

    form_label("Contact Number", 2, 0)
    contact_number = form_entry(2, 1)

    form_label("Manager ID", 2, 2)
    manager_id = form_entry(2, 3)

    form_label("Status", 3, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Active", "Inactive"],
        state="readonly",
        width=25
    )
    status.grid(row=3, column=1, padx=10, pady=8)
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
            "branch_id", "branch", "area",
            "city", "status", "contact", "manager"
        ),
        show="headings"
    )

    headings = [
        ("branch_id", "Gym ID"),
        ("branch", "Branch Name"),
        ("area", "Area"),
        ("city", "City"),
        ("status", "Status"),
        ("contact", "Contact Number"),
        ("manager", "Manager ID")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        branch_id.delete(0, tk.END)
        branch_name.delete(0, tk.END)
        city.set("")
        area.set("")
        contact_number.delete(0, tk.END)
        manager_id.delete(0, tk.END)
        status.set("Active")

    def load_branches_table():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT branch_id, branch_name, area, city,
                          status, contact_number, manager_id
                   FROM branches"""
        conditions = []
        params = []

        # 🔹 FILTER (City)
        if city_filter.get() != "All":
            conditions.append("city=%s")
            params.append(city_filter.get())

        # 🔹 SEARCH (Branch Name)
        search_text = search_entry.get().strip()
        if search_text:
            conditions.append("branch_name LIKE %s")
            params.append(f"%{search_text}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY branch_id DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_branch():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO branches
               (branch_name, area, city, status, contact_number, manager_id)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                branch_name.get(),
                area.get(),
                city.get(),
                status.get(),
                contact_number.get(),
                manager_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Gym branch added successfully")
        clear_form()
        load_branches_table()

    def update_branch():
        if not branch_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE branches SET
               branch_name=%s,
               area=%s,
               city=%s,
               status=%s,
               contact_number=%s,
               manager_id=%s
               WHERE branch_id=%s""",
            (
                branch_name.get(),
                area.get(),
                city.get(),
                status.get(),
                contact_number.get(),
                manager_id.get(),
                branch_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Gym branch updated successfully")
        load_branches_table()

    def delete_branch():
        if not branch_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this gym branch?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM branches WHERE branch_id=%s", (branch_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_branches_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        branch_id.insert(0, data[0])
        branch_name.insert(0, data[1])
        area.set(data[2])
        city.set(data[3])
        status.set(data[4])
        contact_number.insert(0, data[5])
        manager_id.insert(0, data[6])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add Branch", "#2196F3", add_branch)
    action_btn("Update", "#FF9800", update_branch)
    action_btn("Delete", "#F44336", delete_branch)
    action_btn("Clear", "#607D8B", clear_form)

    # 🔹 Load initial data
    load_branches_table()
