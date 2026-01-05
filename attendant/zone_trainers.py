import tkinter as tk
from tkinter import ttk
from database_db import get_connection

# ================= ZONE TRAINERS PAGE =================
def load_zone_trainers(main_frame, attendant_id):
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
        text="My Zone Trainers",
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
        "trainer_id",
        "name",
        "email",
        "contact",
        "specialization",
        "experience",
        "shift_time",
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
        "trainer_id": "Trainer ID",
        "name": "Name",
        "email": "Email",
        "contact": "Contact",
        "specialization": "Specialization",
        "experience": "Experience (Years)",
        "shift_time": "Shift Time",
        "status": "Status"
    }

    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, anchor="center", width=150)

    # ---------- Load Data ----------
    load_zone_trainers_data(tree, attendant_id)


# ================= FETCH DATA =================
def load_zone_trainers_data(tree, attendant_id):
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

    # Fetch trainers of that zone
    cursor.execute(
        """
        SELECT 
            trainer_id,
            name,
            email,
            emergency_contact,
            specialization,
            experience_years,
            shift_time,
            status
        FROM trainers
        WHERE zone_id = %s
        """,
        (zone_id,)
    )

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=(
            row["trainer_id"],
            row["name"],
            row["email"],
            row["emergency_contact"],
            row["specialization"],
            row["experience_years"],
            row["shift_time"],
            row["status"]
        ))

    conn.close()
