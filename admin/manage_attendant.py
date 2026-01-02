import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection

def load_manage_attendants(content):
    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Attendants",
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
        text="Filter by Status:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    status_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Active", "Inactive"],
        state="readonly",
        width=18
    )
    status_filter.set("All")
    status_filter.pack(side="left", padx=(0, 15))

    # 🔹 Search Label + Entry
    tk.Label(
        filter_frame,
        text="Search by Attendant ID:",
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
    #     command=lambda: load_attendants_table()
    # ).pack(side="left")

    # 🔹 Live search & filter
    search_entry.bind("<KeyRelease>", lambda e: load_attendants_table())
    status_filter.bind("<<ComboboxSelected>>", lambda e: load_attendants_table())

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
    form_label("Attendant ID", 0, 0)
    attendant_id = form_entry(0, 1)

    form_label("Shift Time", 0, 2)
    shift_time = form_entry(0, 3)

    form_label("Gym ID", 1, 0)
    gym_id = form_entry(1, 1)

    form_label("Zone ID", 1, 2)
    zone_id = form_entry(1, 3)

    form_label("Qualification", 2, 0)
    qualification = form_entry(2, 1)

    form_label("Emergency Contact", 2, 2)
    emergency_contact = form_entry(2, 3)

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
        columns=("id", "shift", "gym", "zone", "qualification", "contact", "status"),
        show="headings"
    )

    headings = [
        ("id", "Attendant ID"),
        ("shift", "Shift Time"),
        ("gym", "Gym ID"),
        ("zone", "Zone ID"),
        ("qualification", "Qualification"),
        ("contact", "Emergency Contact"),
        ("status", "Status")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=130)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        attendant_id.delete(0, tk.END)
        shift_time.delete(0, tk.END)
        gym_id.delete(0, tk.END)
        zone_id.delete(0, tk.END)
        qualification.delete(0, tk.END)
        emergency_contact.delete(0, tk.END)
        status.set("Active")

    def load_attendants_table():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT attendant_id, shift_time, gym_id, zone_id, qualification,
                          emergency_contact, status
                   FROM attendants"""
        conditions = []
        params = []

        # 🔹 FILTER (Status)
        if status_filter.get() != "All":
            conditions.append("status=%s")
            params.append(status_filter.get())

        # 🔹 SEARCH (Attendant ID)
        search_text = search_entry.get().strip()
        if search_text:
            conditions.append("attendant_id LIKE %s")
            params.append(f"%{search_text}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY attendant_id DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_attendant():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO attendants
               (shift_time, gym_id, zone_id, qualification, emergency_contact, status)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                shift_time.get(),
                gym_id.get(),
                zone_id.get(),
                qualification.get(),
                emergency_contact.get(),
                status.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Attendant added successfully")
        clear_form()
        load_attendants_table()

    def update_attendant():
        if not attendant_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE attendants SET
               shift_time=%s,
               gym_id=%s,
               zone_id=%s,
               qualification=%s,
               emergency_contact=%s,
               status=%s
               WHERE attendant_id=%s""",
            (
                shift_time.get(),
                gym_id.get(),
                zone_id.get(),
                qualification.get(),
                emergency_contact.get(),
                status.get(),
                attendant_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Attendant updated successfully")
        load_attendants_table()

    def delete_attendant():
        if not attendant_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this attendant?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM attendants WHERE attendant_id=%s", (attendant_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_attendants_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        attendant_id.insert(0, data[0])
        shift_time.insert(0, data[1])
        gym_id.insert(0, data[2])
        zone_id.insert(0, data[3])
        qualification.insert(0, data[4])
        emergency_contact.insert(0, data[5])
        status.set(data[6])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add Attendant", "#2196F3", add_attendant)
    action_btn("Update", "#FF9800", update_attendant)
    action_btn("Delete", "#F44336", delete_attendant)
    action_btn("Clear", "#607D8B", clear_form)

    # ================= LOAD INITIAL DATA =================
    load_attendants_table()
