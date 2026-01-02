import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection

def load_manage_appointments(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Appointments",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    # Label for filter
    tk.Label(filter_frame, text="Filter by Appointment Type:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold"))\
        .pack(side="left", padx=(0,5))

    type_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Personal Training", "Nutrition", "Yoga", "Physiotherapy"],
        state="readonly",
        width=20
    )
    type_filter.set("All")
    type_filter.pack(side="left", padx=(0, 15))

    # Label for search
    tk.Label(filter_frame, text="Search by Appointment ID:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold"))\
        .pack(side="left", padx=(0,5))

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=(0, 10))

    # ================= FORM =================
    form_frame = tk.Frame(content, bg="#252540")
    form_frame.pack(fill="x", padx=30, pady=20)

    def form_label(text, r, c):
        tk.Label(form_frame, text=text, bg="#252540", fg="white")\
            .grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def form_entry(r, c):
        e = tk.Entry(form_frame, width=28)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    # ========== FORM FIELDS ==========
    form_label("Appointment ID", 0, 0)
    appointment_id = form_entry(0, 1)

    form_label("Member ID", 0, 2)
    member_id = form_entry(0, 3)

    form_label("Appointment Date (YYYY-MM-DD)", 1, 0)
    appointment_date = form_entry(1, 1)

    form_label("Time Slot", 1, 2)
    time_slot = ttk.Combobox(
        form_frame,
        values=[
            "06:00 AM - 07:00 AM",
            "07:00 AM - 08:00 AM",
            "08:00 AM - 09:00 AM",
            "09:00 AM - 10:00 AM",
            "10:00 AM - 11:00 AM",
            "11:00 AM - 12:00 PM",
            "12:00 PM - 01:00 PM",
            "01:00 PM - 02:00 PM",
            "02:00 PM - 03:00 PM",
            "03:00 PM - 04:00 PM",
            "04:00 PM - 05:00 PM",
        ],
        state="readonly",
        width=25
    )
    time_slot.grid(row=1, column=3, padx=10, pady=8)
    time_slot.set("06:00 AM - 07:00 AM")

    form_label("Notes", 2, 0)
    notes = form_entry(2, 1)

    form_label("Appointment Type", 2, 2)
    appointment_type = ttk.Combobox(
        form_frame,
        values=["Personal Training", "Nutrition", "Yoga", "Physiotherapy"],
        state="readonly",
        width=25
    )
    appointment_type.grid(row=2, column=3, padx=10, pady=8)
    appointment_type.set("Personal Training")

    form_label("Status", 3, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Scheduled", "Pending", "Cancelled", "Completed"],
        state="readonly",
        width=25
    )
    status.grid(row=3, column=1, padx=10, pady=8)
    status.set("Scheduled")

    form_label("Cancel Reason", 3, 2)
    cancel_reason = form_entry(3, 3)

    form_label("Cancelled By", 4, 0)
    cancelled_by = form_entry(4, 1)

    form_label("Cancelled At", 4, 2)
    cancelled_at = form_entry(4, 3)

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
            "appointment_id", "member_id", "appointment_date", "time_slot",
            "notes", "appointment_type", "status", "cancel_reason",
            "cancelled_by", "cancelled_at"
        ),
        show="headings"
    )

    headings = [
        ("appointment_id", "Appointment ID"),
        ("member_id", "Member ID"),
        ("appointment_date", "Date"),
        ("time_slot", "Time Slot"),
        ("notes", "Notes"),
        ("appointment_type", "Appointment Type"),
        ("status", "Status"),
        ("cancel_reason", "Cancel Reason"),
        ("cancelled_by", "Cancelled By"),
        ("cancelled_at", "Cancelled At"),
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=130)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        for e in [
            appointment_id, member_id, appointment_date, notes,
            cancel_reason, cancelled_by, cancelled_at
        ]:
            e.delete(0, tk.END)
        time_slot.set("06:00 AM - 07:00 AM")
        appointment_type.set("Personal Training")
        status.set("Scheduled")

    # ================= LIVE TABLE LOADING =================
    def load_appointments_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT appointment_id, member_id, appointment_date,
                   time_slot, notes, appointment_type, status,
                   cancel_reason, cancelled_by, cancelled_at
                   FROM appointments"""
        params = []

        where_clauses = []

        # Filter by Appointment Type
        if type_filter.get() != "All":
            where_clauses.append("appointment_type=%s")
            params.append(type_filter.get())

        # Search by Appointment ID
        if search_entry.get():
            where_clauses.append("appointment_id LIKE %s")
            params.append(f"%{search_entry.get()}%")

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    # Bind live search/filter
    search_entry.bind("<KeyRelease>", lambda e: load_appointments_table())
    type_filter.bind("<<ComboboxSelected>>", lambda e: load_appointments_table())

    def add_appointment():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO appointments
               (member_id, appointment_date, time_slot, notes,
                appointment_type, status, cancel_reason, cancelled_by, cancelled_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                member_id.get(), appointment_date.get(), time_slot.get(), notes.get(),
                appointment_type.get(), status.get(), cancel_reason.get(),
                cancelled_by.get(), cancelled_at.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Appointment added successfully")
        clear_form()
        load_appointments_table()

    def update_appointment():
        if not appointment_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE appointments SET
               member_id=%s, appointment_date=%s, time_slot=%s, notes=%s,
               appointment_type=%s, status=%s, cancel_reason=%s,
               cancelled_by=%s, cancelled_at=%s
               WHERE appointment_id=%s""",
            (
                member_id.get(), appointment_date.get(), time_slot.get(), notes.get(),
                appointment_type.get(), status.get(), cancel_reason.get(),
                cancelled_by.get(), cancelled_at.get(), appointment_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Appointment updated successfully")
        load_appointments_table()

    def delete_appointment():
        if not appointment_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this appointment?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM appointments WHERE appointment_id=%s", (appointment_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_appointments_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        appointment_id.insert(0, data[0])
        member_id.insert(0, data[1])
        appointment_date.insert(0, data[2])
        time_slot.set(data[3])
        notes.insert(0, data[4])
        appointment_type.set(data[5])
        status.set(data[6])
        cancel_reason.insert(0, data[7])
        cancelled_by.insert(0, data[8])
        cancelled_at.insert(0, data[9])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTONS =================
    action_btn("Add Appointment", "#2196F3", add_appointment)
    action_btn("Update", "#FF9800", update_appointment)
    action_btn("Delete", "#F44336", delete_appointment)
    action_btn("Clear", "#607D8B", clear_form)

    # Initial load
    load_appointments_table()
