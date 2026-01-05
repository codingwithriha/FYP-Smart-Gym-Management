import tkinter as tk
from tkinter import ttk, messagebox
from database_db import get_connection
from datetime import datetime

# ================= COLORS =================
BG = "#1e1e2f"
CARD_BG = "#2f2f44"
LEFT_BG = "#2a2a3d"
RIGHT_BG = "#2a2a3d"
PRIMARY = "#7c5dfa"
TEXT = "#ffffff"
MUTED = "#b5b5d6"


def load_zone_equipment(parent_frame, attendant_id):
    """Zone Equipment Page: Left TreeView + Right Issue Form"""

    # Clear previous widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # ------------------ Fetch Attendant Zone ------------------
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT zone_id FROM attendants WHERE attendant_id=%s",
        (attendant_id,)
    )
    attendant = cursor.fetchone()
    if not attendant:
        conn.close()
        return
    zone_id = attendant["zone_id"]
    conn.close()

    # ------------------ Main Frame ------------------
    main_frame = tk.Frame(parent_frame, bg=BG)
    main_frame.pack(fill="both", expand=True)

    # ------------------ LEFT FRAME (Equipment TreeView) ------------------
    left = tk.Frame(main_frame, bg=LEFT_BG)
    left.pack(side="left", fill="both", expand=True, padx=(15, 10), pady=15)

    # Top Bar
    top_bar = tk.Frame(left, bg=PRIMARY, height=50)
    top_bar.pack(fill="x")
    tk.Label(top_bar, text="My Zone Equipment", bg=PRIMARY, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(expand=True)

    # TreeView Style
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2a2a3d", foreground="#ffffff",
                    rowheight=30, fieldbackground="#2a2a3d", borderwidth=0)
    style.configure("Treeview.Heading", background=PRIMARY, foreground="#ffffff",
                    font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", PRIMARY)],
              foreground=[("selected", "#ffffff")])

    # TreeView Frame
    tree_frame = tk.Frame(left, bg=LEFT_BG, bd=1, relief="ridge")
    tree_frame.pack(fill="both", expand=True, pady=(10, 0))

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    columns = ("equipment_id", "name", "quantity", "purchase_date", "status", "zone_id")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set)
    tree_scroll.config(command=tree.yview)

    # Define headings
    headings = {
        "equipment_id": "Equipment ID",
        "name": "Name",
        "quantity": "Quantity",
        "purchase_date": "Purchase Date",
        "status": "Status",
        "zone_id": "Zone ID"
    }

    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, anchor="center", width=120)
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # ------------------ RIGHT FRAME (Report Equipment Issue Form) ------------------
    right = tk.Frame(main_frame, bg=RIGHT_BG)
    right.pack(side="left", fill="both", expand=True, padx=(10, 15), pady=15)

    # Top Bar
    form_top = tk.Frame(right, bg=PRIMARY, height=50)
    form_top.pack(fill="x")
    tk.Label(form_top, text="Report Equipment Issue", bg=PRIMARY, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(expand=True)

    # Form Frame
    form_frame = tk.Frame(right, bg=RIGHT_BG, bd=1, relief="ridge", padx=15, pady=15)
    form_frame.pack(fill="both", expand=True, pady=(10, 0))

    # 1️⃣ Select Equipment
    tk.Label(form_frame, text="Select Equipment:", bg=RIGHT_BG, fg=MUTED,
             font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 2))
    equipment_var = tk.StringVar()
    equipment_dropdown = ttk.Combobox(form_frame, textvariable=equipment_var, state="readonly")
    equipment_dropdown.pack(fill="x", pady=(0, 10))

    # Load equipment for dropdown
    def load_equipment_dropdown():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT equipment_id, name
            FROM equipment
            WHERE zone_id=%s
        """, (zone_id,))
        rows = cursor.fetchall()
        conn.close()
        options = [f"{row['equipment_id']} | {row['name']}" for row in rows]
        equipment_dropdown['values'] = options
        if options:
            equipment_dropdown.current(0)
    load_equipment_dropdown()

    # 2️⃣ Issue Type Dropdown
    tk.Label(form_frame, text="Issue Type:", bg=RIGHT_BG, fg=MUTED,
             font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 2))
    issue_var = tk.StringVar()
    issue_dropdown = ttk.Combobox(form_frame, textvariable=issue_var, state="readonly")
    issue_dropdown['values'] = ["Not Working", "Damaged", "Electrical Issue", "Noise Problem", "Maintenance Required"]
    issue_dropdown.pack(fill="x", pady=(0, 10))
    issue_dropdown.current(0)

    # 3️⃣ Description Text
    tk.Label(form_frame, text="Description:", bg=RIGHT_BG, fg=MUTED,
             font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 2))
    description_text = tk.Text(form_frame, height=5, bg="#2a2a3d", fg="#ffffff", insertbackground="#ffffff")
    description_text.pack(fill="x", pady=(0, 10))

    # ------------------ REPORT BUTTON ------------------
    def report_issue():
        equipment_sel = equipment_var.get()
        issue_type = issue_var.get()
        description = description_text.get("1.0", "end").strip()

        if not equipment_sel or not description:
            messagebox.showerror("Error", "Please select equipment and write a description")
            return

        equipment_id = int(equipment_sel.split("|")[0].strip())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO equipment_issues
            (equipment_id, issue_type, description, reported_by, created_at, status)
            VALUES (%s, %s, %s, %s, NOW(), 'Pending')
        """, (equipment_id, issue_type, description, attendant_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Equipment issue reported successfully")
        description_text.delete("1.0", "end")
        load_equipment_dropdown()

    tk.Button(form_frame, text="Report Issue", bg=PRIMARY, fg=TEXT,
              font=("Segoe UI", 12, "bold"), relief="flat",
              command=report_issue).pack(fill="x", pady=10)

    # ------------------ LOAD LEFT TREEVIEW DATA ------------------
    def load_equipment_tree():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT equipment_id, name, quantity, purchase_date, status, zone_id
            FROM equipment
            WHERE zone_id=%s
        """, (zone_id,))
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", "end", values=(
                r["equipment_id"], r["name"], r["quantity"],
                r["purchase_date"].strftime("%Y-%m-%d") if r["purchase_date"] else "",
                r["status"], r["zone_id"]
            ))

    load_equipment_tree()
