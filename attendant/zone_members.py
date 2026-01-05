import tkinter as tk
from tkinter import ttk
from database_db import get_connection

# ================= ZONE MEMBERS PAGE =================
def load_zone_members(main_frame, attendant_id):
    # Clear parent frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # ---------- Main Container ----------
    main_frame = tk.Frame(main_frame, bg="#1e1e2f")
    main_frame.pack(fill="both", expand=True)

    # ---------- Top Bar ----------
    top_bar = tk.Frame(main_frame, bg="#7c5dfa", height=55)
    top_bar.pack(fill="x")
    top_bar.pack_propagate(False)

    title = tk.Label(
        top_bar,
        text="My Zone Members",
        bg="#7c5dfa",
        fg="#ffffff",
        font=("Segoe UI", 16, "bold")
    )
    title.pack(expand=True)

    # ---------- Content Frame ----------
    content_frame = tk.Frame(main_frame, bg="#1e1e2f", padx=20, pady=20)
    content_frame.pack(fill="both", expand=True)

    # ---------- Treeview Style ----------
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

    # ---------- Treeview ----------
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

    tree_frame = tk.Frame(content_frame, bg="#1e1e2f")
    tree_frame.pack(fill="both", expand=True)

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        yscrollcommand=tree_scroll.set
    )
    tree.pack(fill="both", expand=True)

    tree_scroll.config(command=tree.yview)

    headings = {
        "member_id": "Member ID",
        "name": "Name",
        "email": "Email",
        "contact": "Emergency Contact",
        "membership_type": "Membership Type",
        "start_date": "Start Date",
        "end_date": "End Date",
        "status": "Status"
    }

    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, anchor="center", width=140)

    # ---------- Load Data ----------
    load_zone_members_data(tree, attendant_id)


# ================= FETCH DATA =================
def load_zone_members_data(tree, attendant_id):
    for row in tree.get_children():
        tree.delete(row)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get attendant zone
    cursor.execute(
        "SELECT zone_id FROM attendants WHERE attendant_id = %s",
        (attendant_id,)
    )
    attendant = cursor.fetchone()

    if not attendant:
        return

    zone_id = attendant["zone_id"]

    # Fetch members of that zone
    cursor.execute(
        """
        SELECT 
            member_id,
            name,
            email,
            emergency_contact,
            membership_type,
            membership_start_date,
            membership_end_date,
            status
        FROM members
        WHERE zone_id = %s
        """,
        (zone_id,)
    )

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=(
            row["member_id"],
            row["name"],
            row["email"],
            row["emergency_contact"],
            row["membership_type"],
            row["membership_start_date"],
            row["membership_end_date"],
            row["status"]
        ))

    conn.close()
