import tkinter as tk
from tkinter import messagebox
from database_db import get_connection

# ================= TRAINER PROFILE PAGE =================
def load_profile(parent, trainer_id):

    # Clear main frame
    for widget in parent.winfo_children():
        widget.destroy()

    # ---------------- THEME ----------------
    BG = "#1e1e2f"
    CARD = "#2a2a3f"
    ACCENT = "#7c5dfa"
    TEXT = "#ffffff"
    INPUT_BG = "#33334d"
    BORDER = "#444466"

    parent.configure(bg=BG)

    # ---------------- MAIN CONTAINER ----------------
    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True, padx=25, pady=25)

    tk.Label(
        main,
        text="My Profile",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", pady=(0, 20))

    card = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    card.pack(fill="both", padx=10, pady=10)

    # ---------------- FETCH TRAINER DATA ----------------
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT name, email, emergency_contact,
                   specialization, qualification,
                   experience_years, shift_time, status
            FROM trainers
            WHERE trainer_id = %s
        """, (trainer_id,))
        trainer = cursor.fetchone()

        if not trainer:
            messagebox.showerror("Error", "Trainer not found")
            return

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    # ---------------- FORM ----------------
    def label(text, r):
        tk.Label(card, text=text, bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).grid(row=r, column=0, sticky="w", padx=20, pady=10)

    def entry(value, r, readonly=True):
        e = tk.Entry(card, bg=INPUT_BG, fg=TEXT, relief="flat", width=30)
        e.grid(row=r, column=1, padx=20, pady=10)
        e.insert(0, value if value else "")
        if readonly:
            e.config(state="readonly")
        return e

    # Editable
    label("Username", 0)
    name_entry = entry(trainer["name"], 0, readonly=False)

    label("Phone Number", 1)
    phone_entry = entry(trainer["emergency_contact"], 1, readonly=False)

    # Read-only
    label("Email", 2)
    entry(trainer["email"], 2)

    label("Specialization", 3)
    entry(trainer["specialization"], 3)

    label("Qualification", 4)
    entry(trainer["qualification"], 4)

    label("Experience (Years)", 5)
    entry(trainer["experience_years"], 5)

    label("Shift Time", 6)
    entry(trainer["shift_time"], 6)

    label("Status", 7)
    entry(trainer["status"], 7)

    # ---------------- UPDATE FUNCTION ----------------
    def update_profile():
        name = name_entry.get().strip()
        phone = phone_entry.get().strip()

        if not name or not phone:
            messagebox.showerror("Error", "Username and Phone Number are required")
            return

        try:
            cursor.execute("""
                UPDATE trainers
                SET name=%s, emergency_contact=%s
                WHERE trainer_id=%s
            """, (name, phone, trainer_id))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- BUTTON ----------------
    tk.Button(
        card,
        text="Update Profile",
        bg=ACCENT,
        fg=TEXT,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        pady=8,
        command=update_profile
    ).grid(row=8, column=0, columnspan=2, pady=20)
