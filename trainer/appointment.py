import tkinter as tk
from tkinter import ttk
from database_db import get_connection


def load_appointments(content_frame, trainer_id):

    # -------- CLEAR OLD PAGE --------
    for widget in content_frame.winfo_children():
        widget.destroy()

    content_frame.configure(bg="#1e1e2f")

    # ================== STYLES ==================
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="#2a2a3d",
        foreground="#ffffff",
        rowheight=32,
        fieldbackground="#2a2a3d",
        borderwidth=0,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Treeview.Heading",
        background="#7c5dfa",
        foreground="#ffffff",
        font=("Segoe UI", 10, "bold")
    )

    style.map("Treeview", background=[("selected", "#7c5dfa")])

    # ================== HEADER ==================
    header = tk.Frame(content_frame, bg="#252538", height=80)
    header.pack(fill="x", pady=(0, 10))

    tk.Label(
        header,
        text="Appointments",
        bg="#252538",
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack(anchor="w", padx=20, pady=(15, 5))

    # ================== FILTER BAR ==================
    filter_bar = tk.Frame(content_frame, bg="#1e1e2f")
    filter_bar.pack(fill="x", padx=20, pady=(0, 15))

    tk.Label(
        filter_bar,
        text="Status",
        bg="#1e1e2f",
        fg="#bfbfbf"
    ).pack(side="left")

    status_var = tk.StringVar(value="All")
    status_combo = ttk.Combobox(
        filter_bar,
        textvariable=status_var,
        values=["All", "Pending", "Scheduled", "Completed", "Cancelled"],
        state="readonly",
        width=18
    )
    status_combo.pack(side="left", padx=(10, 20))

    refresh_btn = tk.Button(
        filter_bar,
        text="Refresh",
        bg="#7c5dfa",
        fg="white",
        relief="flat",
        padx=15,
        command=lambda: load_appointments()
    )
    refresh_btn.pack(side="left")

    # ================== TABLE ==================
    table_frame = tk.Frame(content_frame, bg="#1e1e2f")
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    columns = ("member", "date", "time", "activity", "status")

    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    tree.heading("member", text="Member Name")
    tree.heading("date", text="Date")
    tree.heading("time", text="Time")
    tree.heading("activity", text="Activity Type")
    tree.heading("status", text="Status")

    tree.column("member", width=220)
    tree.column("date", width=120, anchor="center")
    tree.column("time", width=180, anchor="center")
    tree.column("activity", width=200)
    tree.column("status", width=120, anchor="center")

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ================== LOAD DATA ==================
    def load_appointments():
        tree.delete(*tree.get_children())

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                m.name AS member_name,
                a.appointment_date,
                a.time_slot,
                a.appointment_type,
                a.status
            FROM appointments a
            JOIN members m ON a.member_id = m.member_id
            WHERE a.trainer_id = %s
        """
        params = [trainer_id]

        if status_var.get() != "All":
            query += " AND a.status = %s"
            params.append(status_var.get())

        query += " ORDER BY a.appointment_date ASC"

        cursor.execute(query, params)
        for row in cursor.fetchall():
            tree.insert("", "end", values=(
                row["member_name"],
                row["appointment_date"],
                row["time_slot"],
                row["appointment_type"],
                row["status"]
            ))

        conn.close()

    status_combo.bind("<<ComboboxSelected>>", lambda e: load_appointments())
    load_appointments()
