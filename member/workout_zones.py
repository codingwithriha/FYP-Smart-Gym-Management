import tkinter as tk
from tkinter import ttk
from database_db import get_connection

def load_workout_zones_page(content):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Workout Zones",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(10, 20))

    # ---------------- TREEVIEW + SCROLLBAR FRAME ----------------
    tree_frame = tk.Frame(content, bg="#1f1b2e")
    tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ---------------- TREEVIEW ----------------
    columns = ("zone_name", "zone_type", "floor_number", "announcements")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    # Column headings
    tree.heading("zone_name", text="Zone")
    tree.heading("zone_type", text="Type")
    tree.heading("floor_number", text="Floor")
    tree.heading("announcements", text="Announcement")

    # Column widths
    tree.column("zone_name", width=150, anchor="center")
    tree.column("zone_type", width=120, anchor="center")
    tree.column("floor_number", width=80, anchor="center")
    tree.column("announcements", width=250, anchor="w")

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
            SELECT zone_name, zone_type, floor_number, announcements
            FROM workout_zones
            ORDER BY zone_name ASC
        """
        cursor.execute(query)
        zones = cursor.fetchall()
        conn.close()

        # Insert data into Treeview
        for zone in zones:
            tree.insert("", "end", values=zone)

    except Exception as e:
        tk.Label(
            content,
            text=f"Error fetching workout zones: {str(e)}",
            bg="#1f1b2e",
            fg="red",
            font=("Segoe UI", 12)
        ).pack(pady=20)
