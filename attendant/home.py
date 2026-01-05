import tkinter as tk
from tkinter import ttk
from database_db import get_connection

# ================= COLORS =================
BG = "#1e1e2f"
CARD_BG = "#2f2f44"
LEFT_BG = "#2a2a3d"
RIGHT_BG = "#2a2a3d"
PRIMARY = "#7c5dfa"
TEXT = "#ffffff"
MUTED = "#b5b5d6"


def load_home(main_frame, attendant_id):

    for widget in main_frame.winfo_children():
        widget.destroy()

    # -------- FETCH ATTENDANT INFO --------
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT name, email, shift_time, zone_id FROM attendants WHERE attendant_id=%s",
        (attendant_id,)
    )
    attendant = cursor.fetchone()
    conn.close()

    name = attendant["name"]
    email = attendant["email"]
    shift = attendant["shift_time"]
    zone_id = attendant["zone_id"]

    # ================= TOP CARDS =================
    cards_frame = tk.Frame(main_frame, bg=BG)
    cards_frame.pack(fill="x", padx=20, pady=(15, 10))

    card_titles = ["Zone Members", "Zone Trainers", "Today's Check-in", "Equipment Issues"]
    card_icons = ["👥", "🏋️", "🕒", "⚙️"]
    card_values = [0, 0, 0, 0]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM members WHERE zone_id=%s", (zone_id,))
    card_values[0] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trainers WHERE zone_id=%s", (zone_id,))
    card_values[1] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM attendance a
        JOIN members m ON m.member_id=a.user_id
        WHERE DATE(a.check_in)=CURDATE() AND m.zone_id=%s
    """, (zone_id,))
    card_values[2] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM equipment_issues")
    card_values[3] = cursor.fetchone()[0]
    conn.close()

    for i in range(4):
        card = tk.Frame(cards_frame, bg=CARD_BG, height=90, bd=1, relief="ridge")
        card.pack(side="left", expand=True, fill="x", padx=8)
        card.pack_propagate(False)

        top = tk.Frame(card, bg=CARD_BG)
        top.pack(fill="x", pady=(10, 0), padx=15)

        tk.Label(top, text=card_icons[i], bg=CARD_BG, fg=PRIMARY,
                 font=("Segoe UI", 20)).pack(side="left")

        tk.Label(top, text=card_titles[i], bg=CARD_BG, fg=MUTED,
                 font=("Segoe UI", 11)).pack(side="left", padx=8)

        tk.Label(
            card, text=str(card_values[i]),
            bg=CARD_BG, fg=TEXT,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=18, pady=(5, 10))

    # ================= MAIN CONTENT =================
    body = tk.Frame(main_frame, bg=BG)
    body.pack(fill="both", expand=True, padx=20, pady=10)

    # ================= LEFT COLUMN =================
    left = tk.Frame(body, bg=LEFT_BG)
    left.pack(side="left", fill="both", expand=True, padx=(0, 10))

    info = tk.Frame(left, bg=LEFT_BG, bd=1, relief="ridge")
    info.pack(fill="x", padx=15, pady=15)

    tk.Label(info, text="Attendant Info", bg=LEFT_BG, fg=TEXT,
             font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

    for label, value in [("Name", name), ("Email", email), ("Shift", shift)]:
        row = tk.Frame(info, bg=LEFT_BG)
        row.pack(anchor="w", padx=12, pady=2)
        tk.Label(row, text=f"{label}:", bg=LEFT_BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Label(row, text=value, bg=LEFT_BG, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=5)

    actions = tk.Frame(left, bg=LEFT_BG, bd=1, relief="ridge")
    actions.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    tk.Label(actions, text="Quick Actions", bg=LEFT_BG, fg=TEXT,
             font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=10)

    for act in ["Mark Attendance", "Report Equipment Issue"]:
        tk.Button(
            actions, text=act,
            bg=PRIMARY, fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat", height=2
        ).pack(fill="x", padx=20, pady=6)

    # ================= RIGHT COLUMN =================
    right = tk.Frame(body, bg=RIGHT_BG)
    right.pack(side="left", fill="both", expand=True)

    header = tk.Frame(right, bg=RIGHT_BG)
    header.pack(fill="x", padx=15, pady=15)

    tk.Label(header, text="Zone Statistics", bg=RIGHT_BG, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(anchor="w")

    btns = tk.Frame(header, bg=RIGHT_BG)
    btns.pack(anchor="w", pady=8)

    # ================= TREEVIEW STYLE =================
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="#2a2a3d",
        foreground="#ffffff",
        rowheight=30,
        fieldbackground="#2a2a3d",
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background="#7c5dfa",
        foreground="#ffffff",
        font=("Segoe UI", 10, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", "#7c5dfa")],
        foreground=[("selected", "#ffffff")]
    )

    # ================= TREEVIEW =================
    tree_frame = tk.Frame(right, bg=RIGHT_BG, bd=1, relief="ridge")
    tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    columns = ("ID", "Name", "Status")
    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        yscrollcommand=tree_scroll.set
    )
    tree_scroll.config(command=tree.yview)

    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Status", text="Status")

    tree.column("ID", anchor="center", width=100)
    tree.column("Name", anchor="w", width=220)
    tree.column("Status", anchor="center", width=140)

    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # ================= DATA LOADERS =================
    def load_zone_attendance():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.member_id ID, m.name Name, a.check_in Status
            FROM attendance a
            JOIN members m ON m.member_id=a.user_id
            WHERE DATE(a.check_in)=CURDATE() AND m.zone_id=%s
        """, (zone_id,))
        for r in cursor.fetchall():
            tree.insert("", "end", values=(r["ID"], r["Name"], r["Status"]))
        conn.close()

    def load_equipment_status():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT equipment_id ID, name Name, status Status
            FROM equipment
            WHERE zone_id=%s
        """, (zone_id,))
        for r in cursor.fetchall():
            tree.insert("", "end", values=(r["ID"], r["Name"], r["Status"]))
        conn.close()

    tk.Button(
        btns, text="Zone Attendance",
        bg=PRIMARY, fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=load_zone_attendance
    ).pack(side="left", padx=5)

    tk.Button(
        btns, text="Equipment Status",
        bg=PRIMARY, fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=load_equipment_status
    ).pack(side="left", padx=5)

    load_zone_attendance()
