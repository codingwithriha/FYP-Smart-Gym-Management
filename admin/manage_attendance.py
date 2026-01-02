import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_attendance(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Attendance",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(filter_frame, text="Filter by Role:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)
    role_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Admin", "Manager", "Trainer", "Member"],
        state="readonly",
        width=18
    )
    role_filter.set("All")
    role_filter.pack(side="left", padx=5)

    tk.Label(filter_frame, text="Search by Attendance ID:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)
    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=10)

    # tk.Button(
    #     filter_frame,
    #     text="Search",
    #     bg="#4CAF50",
    #     fg="white",
    #     bd=0,
    #     padx=20,
    #     pady=6,
    #     command=lambda: load_attendance_table()
    # ).pack(side="left")

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

    # ================= FORM FIELDS =================
    form_label("Attendance ID", 0, 0)
    attendance_id = form_entry(0, 1)

    form_label("User ID", 0, 2)
    user_id = form_entry(0, 3)

    form_label("Role", 1, 0)
    role = ttk.Combobox(
        form_frame,
        values=["Admin", "Manager", "Trainer", "Member"],
        state="readonly",
        width=25
    )
    role.grid(row=1, column=1, padx=10, pady=8)
    role.set("Member")

    form_label("Date (YYYY-MM-DD)", 1, 2)
    attendance_date = form_entry(1, 3)

    form_label("Check-in Time", 2, 0)
    check_in = form_entry(2, 1)

    form_label("Check-out Time", 2, 2)
    check_out = form_entry(2, 3)

    form_label("Status", 3, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Present", "Absent", "Leave"],
        state="readonly",
        width=25
    )
    status.grid(row=3, column=1, padx=10, pady=8)
    status.set("Present")

    # ================= BUTTONS =================
    btn_frame = tk.Frame(content, bg="#1e1e2f")
    btn_frame.pack(anchor="w", padx=30, pady=15)

    def action_btn(text, color, cmd):
        tk.Button(btn_frame, text=text, bg=color, fg="white",
                  bd=0, padx=18, pady=8, command=cmd)\
            .pack(side="left", padx=5)

    # ================= TABLE =================
    table_frame = tk.Frame(content, bg="#2f2f4f")
    table_frame.pack(fill="both", expand=True, padx=30, pady=20)

    columns = ("id", "user_id", "role", "date", "check_in", "check_out", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=130)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        attendance_id.delete(0, tk.END)
        user_id.delete(0, tk.END)
        role.set("Member")
        attendance_date.delete(0, tk.END)
        check_in.delete(0, tk.END)
        check_out.delete(0, tk.END)
        status.set("Present")

    def load_attendance_table():
        tree.delete(*tree.get_children())

        conn = get_connection()
        cur = conn.cursor()

        query = "SELECT attendance_id, user_id, role, date, check_in, check_out, status FROM attendance"
        conditions = []
        params = []

        # 🔹 Filter by role
        if role_filter.get() != "All":
            conditions.append("role=%s")
            params.append(role_filter.get())

        # 🔹 Search by Attendance ID
        search_text = search_entry.get().strip()
        if search_text:
            conditions.append("attendance_id LIKE %s")
            params.append(f"%{search_text}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY attendance_id DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_attendance():
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO attendance
                   (user_id, role, date, check_in, check_out, status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (user_id.get(), role.get(), attendance_date.get(),
                 check_in.get(), check_out.get(), status.get())
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Attendance added successfully")
            clear_form()
            load_attendance_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_attendance():
        if not attendance_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE attendance SET
               user_id=%s, role=%s, date=%s,
               check_in=%s, check_out=%s, status=%s
               WHERE attendance_id=%s""",
            (user_id.get(), role.get(), attendance_date.get(),
             check_in.get(), check_out.get(), status.get(),
             attendance_id.get())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Attendance updated successfully")
        load_attendance_table()

    def delete_attendance():
        if not attendance_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this attendance record?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM attendance WHERE attendance_id=%s", (attendance_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_attendance_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        attendance_id.insert(0, data[0])
        user_id.insert(0, data[1])
        role.set(data[2])
        attendance_date.insert(0, data[3])
        check_in.insert(0, data[4])
        check_out.insert(0, data[5])
        status.set(data[6])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add Attendance", "#2196F3", add_attendance)
    action_btn("Update", "#FF9800", update_attendance)
    action_btn("Delete", "#F44336", delete_attendance)
    action_btn("Clear", "#607D8B", clear_form)

    # 🔹 LIVE FILTER & SEARCH
    role_filter.bind("<<ComboboxSelected>>", lambda e: load_attendance_table())
    search_entry.bind("<KeyRelease>", lambda e: load_attendance_table())

    # 🔹 Initial load
    load_attendance_table()
