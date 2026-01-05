import tkinter as tk
from tkinter import ttk, messagebox
from database_db import get_connection

def load_attendant_profile(parent, attendant_id):
    # Clear previous content
    for widget in parent.winfo_children():
        widget.destroy()

    # ---------------- COLORS ----------------
    BG = "#1e1e2f"          # Main dark background
    TOPBAR = "#7c5dfa"      # Top bar
    CARD = "#2a2a3f"        # Card background
    ACCENT = "#7c5dfa"       # Labels & button
    LABEL = "#7c5dfa"       # Label text color
    TEXT = "#ffffff"         # Editable input text
    READONLY_BG = "#2f2f47"  # Readonly input background
    INPUT_BG = "#33334d"     # Editable input background
    BTN_HOVER = "#6b4ddb"

    parent.configure(bg=BG)

    # ---------------- TOP BAR ----------------
    topbar = tk.Frame(parent, bg=TOPBAR, height=50)
    topbar.pack(fill="x")
    tk.Label(
        topbar, text="Attendant Info", font=("Segoe UI", 16, "bold"),
        bg=TOPBAR, fg=TEXT
    ).pack(expand=True)  # centered

    # ---------------- MAIN FRAME ----------------
    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    # ---------------- FORMS CONTAINER ----------------
    forms = tk.Frame(main, bg=BG)
    forms.pack(fill="x")
    forms.columnconfigure(0, weight=1)
    forms.columnconfigure(1, weight=1)

    # ---------------- CARD CREATOR ----------------
    def create_card(parent, title):
        card = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1, highlightbackground="#444466")
        tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), bg=CARD, fg=ACCENT)\
            .pack(anchor="w", padx=20, pady=(15, 20))  # add spacing below heading
        body = tk.Frame(card, bg=CARD)
        body.pack(fill="both", expand=True, padx=20, pady=10)
        return card, body

    # ---------------- LEFT & RIGHT CARDS ----------------
    left_card, left_body = create_card(forms, "Basic Information")
    left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
    right_card, right_body = create_card(forms, "Work Information")
    right_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

    # ---------------- FIELD CREATOR ----------------
    def create_field(parent, label_text, row, editable=False):
        tk.Label(
            parent, text=label_text, bg=CARD, fg=LABEL, font=("Segoe UI", 10, "bold")
        ).grid(row=row, column=0, sticky="w", pady=12)
        bg_color = INPUT_BG if editable else READONLY_BG
        fg_color = TEXT if editable else "#1e1e2f"
        entry = tk.Entry(
            parent, width=30, bg=bg_color, fg=fg_color, relief="flat",
            font=("Segoe UI", 10), justify="left", insertbackground=TEXT
        )
        entry.grid(row=row, column=1, pady=12, padx=5)
        if not editable:
            entry.config(state="readonly")
        return entry

    # ---------------- LEFT FIELDS ----------------
    ent_id = create_field(left_body, "Attendant ID", 0)
    ent_name = create_field(left_body, "Name", 1)
    ent_email = create_field(left_body, "Email", 2, editable=True)
    ent_phone = create_field(left_body, "Phone Number", 3, editable=True)
    ent_qualification = create_field(left_body, "Qualification", 4)

    # ---------------- RIGHT FIELDS ----------------
    ent_shift = create_field(right_body, "Shift Time", 0)
    ent_zone = create_field(right_body, "Assigned Zone", 1)
    ent_branch = create_field(right_body, "Assigned Branch", 2)
    ent_area = create_field(right_body, "Work Area", 3)

    # ---------------- SAFE ENTRY UPDATE ----------------
    def set_entry(entry, value):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value if value else "")
        entry.config(state="readonly")

    # ---------------- FETCH DATA ----------------
    def fetch_data():
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT a.attendant_id, a.name, a.email, a.emergency_contact,
                       a.qualification, a.shift_time,
                       wz.zone_name, b.branch_name, b.area
                FROM attendants a
                LEFT JOIN workout_zones wz ON a.zone_id=wz.zone_id
                LEFT JOIN branches b ON a.gym_id=b.branch_id
                WHERE a.attendant_id=%s
            """, (attendant_id,))

            data = cursor.fetchone()
            if not data:
                messagebox.showerror("Error", "Attendant not found")
                return

            set_entry(ent_id, data["attendant_id"])
            set_entry(ent_name, data["name"])
            ent_email.delete(0, tk.END)
            ent_email.insert(0, data["email"])
            ent_phone.delete(0, tk.END)
            ent_phone.insert(0, data["emergency_contact"])
            set_entry(ent_qualification, data["qualification"])
            set_entry(ent_shift, data["shift_time"])
            set_entry(ent_zone, data["zone_name"])
            set_entry(ent_branch, data["branch_name"])
            set_entry(ent_area, data["area"])

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- UPDATE FUNCTION ----------------
    def update_profile():
        email = ent_email.get().strip()
        phone = ent_phone.get().strip()

        if not email or not phone:
            messagebox.showerror("Validation Error", "Email and Phone Number are required")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE attendants
                SET email=%s, emergency_contact=%s
                WHERE attendant_id=%s
            """, (email, phone, attendant_id))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- BUTTON BELOW LEFT FORM ----------------
    btn_frame = tk.Frame(left_card, bg=CARD)
    btn_frame.pack(fill="x", pady=25, padx=25)  # more spacing from form fields

    update_btn = tk.Button(
        btn_frame, text="Update Email & Phone",
        bg=ACCENT, fg=TEXT, font=("Segoe UI", 11, "bold"),
        relief="flat", padx=20, pady=8,
        activebackground="#6b4ddb", activeforeground=TEXT,
        command=update_profile
    )
    update_btn.pack(anchor="w")  # left side, below form

    # Load data initially
    fetch_data()
