import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_schedules(content):
    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Schedules",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER & SEARCH =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(
        filter_frame,
        text="Filter by Day:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    day_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        state="readonly",
        width=15
    )
    day_filter.set("All")
    day_filter.pack(side="left", padx=(0, 20))

    tk.Label(
        filter_frame,
        text="Search by Schedule ID:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    search_entry = tk.Entry(filter_frame, width=30)
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

    # ================= FORM FIELDS =================
    # Row 0
    form_label("Schedule ID", 0, 0)
    schedule_id = form_entry(0, 1)

    form_label("Trainer ID", 0, 2)
    trainer_id = form_entry(0, 3)

    # Row 1
    form_label("Day of Week", 1, 0)
    day_of_week = ttk.Combobox(
        form_frame,
        values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        state="readonly",
        width=23
    )
    day_of_week.grid(row=1, column=1, padx=10, pady=8)
    day_of_week.set("Monday")

    form_label("Start Time (HH:MM)", 1, 2)
    start_time = form_entry(1, 3)

    # Row 2
    form_label("End Time (HH:MM)", 2, 0)
    end_time = form_entry(2, 1)

    form_label("Activity", 2, 2)
    activity = form_entry(2, 3)

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
        columns=("schedule_id", "trainer_id", "day_of_week", "start_time", "end_time", "activity"),
        show="headings"
    )

    headings = [
        ("schedule_id", "Schedule ID"),
        ("trainer_id", "Trainer ID"),
        ("day_of_week", "Day of Week"),
        ("start_time", "Start Time"),
        ("end_time", "End Time"),
        ("activity", "Activity")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=150 if col != "activity" else 200)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        schedule_id.delete(0, tk.END)
        trainer_id.delete(0, tk.END)
        day_of_week.set("Monday")
        start_time.delete(0, tk.END)
        end_time.delete(0, tk.END)
        activity.delete(0, tk.END)

    def load_schedules_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = "SELECT schedule_id, trainer_id, day_of_week, start_time, end_time, activity FROM schedules"
        params = []
        where = []

        if day_filter.get() != "All":
            where.append("day_of_week=%s")
            params.append(day_filter.get())

        if search_entry.get():
            where.append("schedule_id LIKE %s")
            params.append(f"%{search_entry.get()}%")

        if where:
            query += " WHERE " + " AND ".join(where)

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    # ================= CRUD =================
    def add_schedule():
        if not trainer_id.get() or not start_time.get() or not end_time.get() or not activity.get():
            messagebox.showwarning("Required", "Please fill all required fields")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO schedules (trainer_id, day_of_week, start_time, end_time, activity)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (trainer_id.get(), day_of_week.get(), start_time.get(), end_time.get(), activity.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Schedule added successfully")
        clear_form()
        load_schedules_table()

    def update_schedule():
        if not schedule_id.get():
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE schedules SET
            trainer_id=%s,
            day_of_week=%s,
            start_time=%s,
            end_time=%s,
            activity=%s
            WHERE schedule_id=%s
            """,
            (trainer_id.get(), day_of_week.get(), start_time.get(), end_time.get(), activity.get(), schedule_id.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Schedule updated successfully")
        load_schedules_table()

    def delete_schedule():
        if not schedule_id.get():
            return

        if not messagebox.askyesno("Confirm", "Delete this schedule?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM schedules WHERE schedule_id=%s",
            (schedule_id.get(),)
        )
        conn.commit()
        conn.close()
        clear_form()
        load_schedules_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return

        data = tree.item(selected)["values"]
        clear_form()
        schedule_id.insert(0, data[0])
        trainer_id.insert(0, data[1])
        day_of_week.set(data[2])
        start_time.insert(0, data[3])
        end_time.insert(0, data[4])
        activity.insert(0, data[5])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= LIVE SEARCH & FILTER =================
    search_entry.bind("<KeyRelease>", lambda e: load_schedules_table())
    day_filter.bind("<<ComboboxSelected>>", lambda e: load_schedules_table())

    # ================= BUTTONS =================
    action_btn("Add Schedule", "#2196F3", add_schedule)
    action_btn("Update", "#FF9800", update_schedule)
    action_btn("Delete", "#F44336", delete_schedule)
    action_btn("Clear", "#607D8B", clear_form)

    load_schedules_table()
