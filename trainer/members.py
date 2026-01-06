import tkinter as tk
from tkinter import ttk
from datetime import date
from database_db import get_connection

# ================= COLORS =================
BG = "#1e1e2f"
SIDEBAR_BG = "#1b1b2f"
PRIMARY = "#7c5dfa"
TEXT = "#ffffff"
MUTED = "#b5b5d6"
INPUT_BG = "#2a2a3d"
ROW_ALT = "#252536"

def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()

def load_members(frame, trainer_id):
    """Load 'My Members' Page for Trainer"""
    clear_frame(frame)

    # ------------------- Top Label -------------------
    tk.Label(
        frame,
        text="👥 My Members",
        bg=BG,
        fg=PRIMARY,
        font=("Segoe UI", 20, "bold")
    ).pack(pady=20)

    # ------------------- Treeview Style -------------------
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
        background=[("selected", "#7c5dfa")]
    )

    # ------------------- Treeview -------------------
    columns = (
        "member_id",
        "name",
        "email",
        "contact",
        "membership_type",
        "start_date",
        "end_date",
        "status"
    )

    tree_frame = tk.Frame(frame, bg=BG)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    headings = ["ID", "Name", "Email", "Contact", "Membership", "Start Date", "End Date", "Status"]
    for col, hd in zip(columns, headings):
        tree.heading(col, text=hd)
        tree.column(col, anchor="center", width=120)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    # ------------------- Alternate Row Colors -------------------
    def tag_rows():
        for i, item in enumerate(tree.get_children()):
            tree.item(item, tags=("evenrow",) if i % 2 == 0 else ("oddrow",))
        tree.tag_configure("evenrow", background=ROW_ALT)
        tree.tag_configure("oddrow", background=BG)
    tag_rows()

    # ------------------- Load Data from DB -------------------
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT member_id, name, email, emergency_contact AS contact,
               membership_type, membership_start_date AS start_date,
               membership_end_date AS end_date, status
        FROM members
        WHERE trainer_id=%s
        ORDER BY name ASC
    """, (trainer_id,))
    rows = cur.fetchall()
    conn.close()

    for r in rows:
        tree.insert("", "end", values=(
            r["member_id"],
            r["name"],
            r["email"] or "",
            r["contact"] or "",
            r["membership_type"],
            r["start_date"].strftime("%Y-%m-%d") if r["start_date"] else "",
            r["end_date"].strftime("%Y-%m-%d") if r["end_date"] else "",
            r["status"]
        ))
    tag_rows()
