import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_trainers(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Trainers",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(filter_frame, text="Filter by Status:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

    status_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Active", "Inactive"],
        state="readonly",
        width=18
    )
    status_filter.set("All")
    status_filter.pack(side="left", padx=5)

    tk.Label(filter_frame, text="Search by Trainer ID:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=10)

    tk.Button(
        filter_frame,
        text="Search",
        bg="#4CAF50",
        fg="white",
        bd=0,
        padx=20,
        pady=6,
        command=lambda: load_trainers_table()
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

    form_label("Trainer ID", 0, 0)
    trainer_id = form_entry(0, 1)

    form_label("Specialization", 0, 2)
    specialization = form_entry(0, 3)

    form_label("Qualification", 1, 0)
    qualification = form_entry(1, 1)

    form_label("Experience (Years)", 1, 2)
    experience_years = form_entry(1, 3)

    form_label("Emergency Contact", 2, 0)
    emergency_contact = form_entry(2, 1)

    form_label("Gym ID", 2, 2)
    gym_id = form_entry(2, 3)

    form_label("Zone ID", 3, 0)
    zone_id = form_entry(3, 1)

    form_label("Shift Time", 3, 2)
    shift_time = form_entry(3, 3)

    form_label("Status", 4, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Active", "Inactive"],
        state="readonly",
        width=25
    )
    status.grid(row=4, column=1, padx=10, pady=8)
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
            "id", "specialization", "qualification", "experience",
            "contact", "gym", "zone", "status", "shift"
        ),
        show="headings"
    )

    headings = [
        ("id", "Trainer ID"),
        ("specialization", "Specialization"),
        ("qualification", "Qualification"),
        ("experience", "Experience"),
        ("contact", "Emergency Contact"),
        ("gym", "Gym ID"),
        ("zone", "Zone ID"),
        ("status", "Status"),
        ("shift", "Shift Time")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=130)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        for e in [trainer_id, specialization, qualification,
                  experience_years, emergency_contact,
                  gym_id, zone_id, shift_time]:
            e.delete(0, tk.END)
        status.set("Active")

    def load_trainers_table():
        tree.delete(*tree.get_children())

        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT trainer_id, specialization, qualification,
                   experience_years, emergency_contact,
                   gym_id, zone_id, status, shift_time
                   FROM trainers"""
        conditions = []
        params = []

        # 🔹 FILTER by Status
        if status_filter.get() != "All":
            conditions.append("status=%s")
            params.append(status_filter.get())

        # 🔹 SEARCH by Trainer ID
        search_text = search_entry.get().strip()
        if search_text:
            conditions.append("trainer_id LIKE %s")
            params.append(f"%{search_text}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY trainer_id DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_trainer():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO trainers
               (specialization, qualification, experience_years,
                emergency_contact, gym_id, zone_id, status, shift_time)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                specialization.get(),
                qualification.get(),
                experience_years.get(),
                emergency_contact.get(),
                gym_id.get(),
                zone_id.get(),
                status.get(),
                shift_time.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Trainer added successfully")
        clear_form()
        load_trainers_table()

    def update_trainer():
        if not trainer_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE trainers SET
               specialization=%s,
               qualification=%s,
               experience_years=%s,
               emergency_contact=%s,
               gym_id=%s,
               zone_id=%s,
               status=%s,
               shift_time=%s
               WHERE trainer_id=%s""",
            (
                specialization.get(),
                qualification.get(),
                experience_years.get(),
                emergency_contact.get(),
                gym_id.get(),
                zone_id.get(),
                status.get(),
                shift_time.get(),
                trainer_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Trainer updated successfully")
        load_trainers_table()

    def delete_trainer():
        if not trainer_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this trainer?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM trainers WHERE trainer_id=%s", (trainer_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_trainers_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        trainer_id.insert(0, data[0])
        specialization.insert(0, data[1])
        qualification.insert(0, data[2])
        experience_years.insert(0, data[3])
        emergency_contact.insert(0, data[4])
        gym_id.insert(0, data[5])
        zone_id.insert(0, data[6])
        status.set(data[7])
        shift_time.insert(0, data[8])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add Trainer", "#2196F3", add_trainer)
    action_btn("Update", "#FF9800", update_trainer)
    action_btn("Delete", "#F44336", delete_trainer)
    action_btn("Clear", "#607D8B", clear_form)

    # 🔹 LIVE FILTER & SEARCH
    status_filter.bind("<<ComboboxSelected>>", lambda e: load_trainers_table())
    search_entry.bind("<KeyRelease>", lambda e: load_trainers_table())

    # 🔹 Initial load
    load_trainers_table()
