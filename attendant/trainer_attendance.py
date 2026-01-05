import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database_db import get_connection

def load_trainer_attendance(parent):
    # Clear previous content
    for widget in parent.winfo_children():
        widget.destroy()

    # ---------------- COLORS ----------------
    BG = "#1e1e2f"
    TOPBAR = "#7c5dfa"
    CARD = "#2a2a3f"
    ACCENT = "#7c5dfa"
    LABEL = "#7c5dfa"
    TEXT = "#ffffff"
    READONLY_BG = "#2f2f47"

    parent.configure(bg=BG)

    # ---------------- MAIN FRAME ----------------
    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True, padx=20, pady=20)
    main.columnconfigure(0, weight=1)
    main.columnconfigure(1, weight=2)

    # ---------------- LEFT FRAME ----------------
    left_frame = tk.Frame(main, bg=BG)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    topbar_left = tk.Frame(left_frame, bg=TOPBAR, height=50)
    topbar_left.pack(fill="x")
    tk.Label(topbar_left, text="Mark Trainer Attendance", font=("Segoe UI", 14, "bold"),
             bg=TOPBAR, fg=TEXT).pack(expand=True)

    form_card = tk.Frame(left_frame, bg=CARD, bd=0, highlightthickness=1, highlightbackground="#444466")
    form_card.pack(fill="both", pady=20, padx=0)
    form_body = tk.Frame(form_card, bg=CARD)
    form_body.pack(fill="both", expand=True, padx=20, pady=20)

    # ---------------- FORM FIELDS ----------------
    tk.Label(form_body, text="Select Trainer:", bg=CARD, fg=LABEL, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=12)
    trainer_cb = ttk.Combobox(form_body, width=27, font=("Segoe UI", 10))
    trainer_cb.grid(row=0, column=1, pady=12, padx=5)

    tk.Label(form_body, text="Date:", bg=CARD, fg=LABEL, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=12)
    ent_date = tk.Entry(form_body, bg=READONLY_BG, fg=BG, font=("Segoe UI", 10), relief="flat", justify="left")
    ent_date.grid(row=1, column=1, pady=12, padx=5)
    ent_date.insert(0, datetime.today().strftime("%Y-%m-%d"))
    ent_date.config(state="readonly")

    tk.Label(form_body, text="Check-in Time:", bg=CARD, fg=LABEL, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=12)
    ent_checkin = tk.Entry(form_body, bg=READONLY_BG, fg=BG, font=("Segoe UI", 10), relief="flat", justify="left")
    ent_checkin.grid(row=2, column=1, pady=12, padx=5)
    ent_checkin.insert(0, datetime.now().strftime("%H:%M:%S"))
    ent_checkin.config(state="readonly")

    # ---------------- BUTTONS ----------------
    btn_frame = tk.Frame(form_body, bg=CARD)
    btn_frame.grid(row=3, column=0, columnspan=2, pady=(20, 10))

    btn_checkin = tk.Button(btn_frame, text="Mark Check-in", bg=ACCENT, fg=TEXT,
                            font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=6)
    btn_checkin.pack(side="left", padx=(0,10))

    btn_checkout = tk.Button(btn_frame, text="Mark Check-out", bg=ACCENT, fg=TEXT,
                             font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=6)
    btn_checkout.pack(side="left")

    

    # ---------------- RIGHT FRAME ----------------
    right_frame = tk.Frame(main, bg=BG)
    right_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))

    topbar_right = tk.Frame(right_frame, bg=TOPBAR, height=50)
    topbar_right.pack(fill="x")
    tk.Label(topbar_right, text="Trainer View History", font=("Segoe UI", 14, "bold"),
             bg=TOPBAR, fg=TEXT).pack(expand=True)

    history_card = tk.Frame(right_frame, bg=CARD, bd=0, highlightthickness=1, highlightbackground="#444466")
    history_card.pack(fill="both", pady=20)

    history_tree = ttk.Treeview(history_card, columns=("date", "trainer", "checkin", "checkout"), show="headings", height=20)
    history_tree.heading("date", text="Date")
    history_tree.heading("trainer", text="Trainer Name")
    history_tree.heading("checkin", text="Check-in Time")
    history_tree.heading("checkout", text="Check-out Time")
    history_tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- DB FUNCTIONS ----------------
    def load_trainers():
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM attendance WHERE role='Trainer' GROUP BY user_id")
            trainers = cursor.fetchall()
            trainer_cb['values'] = [t['user_id'] for t in trainers]
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_history():
        for row in history_tree.get_children():
            history_tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.date, t.name AS trainer_name, a.check_in, a.check_out
                FROM attendance a
                LEFT JOIN trainers t ON a.user_id = t.trainer_id
                WHERE a.role='Trainer'
                ORDER BY a.date DESC, a.check_in DESC
            """)
            for row in cursor.fetchall():
                history_tree.insert("", tk.END, values=(row["date"], row["trainer_name"], row["check_in"], row["check_out"]))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- BUTTON LOGIC ----------------
    def mark_checkin():
        trainer_id = trainer_cb.get()
        if not trainer_id:
            messagebox.showerror("Error", "Select a trainer")
            return
        date_today = ent_date.get()
        time_now = datetime.now().strftime("%H:%M:%S")
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM attendance WHERE user_id=%s AND date=%s AND role='Trainer'", (trainer_id, date_today))
            existing = cursor.fetchone()
            if existing:
                messagebox.showerror("Error", "Trainer already checked in for today")
                return
            cursor.execute("INSERT INTO attendance (user_id, date, role, check_in) VALUES (%s, %s, 'Trainer', %s)", (trainer_id, date_today, time_now))
            conn.commit()
            refresh_history()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_checkout():
        trainer_id = trainer_cb.get()
        if not trainer_id:
            messagebox.showerror("Error", "Select a trainer")
            return
        date_today = ent_date.get()
        time_now = datetime.now().strftime("%H:%M:%S")
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM attendance WHERE user_id=%s AND date=%s AND role='Trainer'", (trainer_id, date_today))
            existing = cursor.fetchone()
            if not existing:
                messagebox.showerror("Error", "Trainer has not checked in today")
                return
            cursor.execute("UPDATE attendance SET check_out=%s WHERE user_id=%s AND date=%s AND role='Trainer'", (time_now, trainer_id, date_today))
            conn.commit()
            refresh_history()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Bind buttons
    btn_checkin.config(command=mark_checkin)
    btn_checkout.config(command=mark_checkout)
    # Initial load
    load_trainers()
    refresh_history()
