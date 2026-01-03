import tkinter as tk
from tkinter import ttk
from database_db import get_connection

def load_appointments_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Appointments",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(10, 20))

    # ---------------- TREEVIEW + SCROLLBAR FRAME ----------------
    tree_frame = tk.Frame(content, bg="#1f1b2e")
    tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ---------------- TREEVIEW ----------------
    columns = ("appointment_id", "appointment_date", "time_slot", "appointment_type", "status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    # Column headings
    tree.heading("appointment_id", text="Appointment ID")
    tree.heading("appointment_date", text="Date")
    tree.heading("time_slot", text="Time")
    tree.heading("appointment_type", text="Type")
    tree.heading("status", text="Status")

    # Column widths
    tree.column("appointment_id", width=120, anchor="center")
    tree.column("appointment_date", width=100, anchor="center")
    tree.column("time_slot", width=100, anchor="center")
    tree.column("appointment_type", width=150, anchor="center")
    tree.column("status", width=100, anchor="center")

    # ---------------- SCROLLBAR ----------------
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    # Pack Treeview and Scrollbar side by side
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="left", fill="y")

    # ---------------- FETCH DATA FROM DB ----------------
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT appointment_id, appointment_date, time_slot, appointment_type, status
            FROM appointments
            WHERE member_id = %s
            ORDER BY appointment_date DESC
        """
        cursor.execute(query, (member_id,))
        appointments = cursor.fetchall()
        conn.close()

        # Insert data
        for appt in appointments:
            tree.insert("", "end", values=appt)

    except Exception as e:
        tk.Label(
            content,
            text=f"Error fetching appointments: {str(e)}",
            bg="#1f1b2e",
            fg="red",
            font=("Segoe UI", 12)
        ).pack(pady=20)
