import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database_db import get_connection

def load_attendance(parent, trainer_id):
    """Trainer marks attendance for their assigned members with professional SaaS UI"""

    # Clear previous content
    for widget in parent.winfo_children():
        widget.destroy()

    # ---------------- COLORS ----------------
    BG = "#1e1e2f"
    CARD_BG = "#2a2a3f"
    ACCENT = "#7c5dfa"
    TEXT = "#ffffff"
    LABEL = "#b5b5d6"
    INPUT_BG = "#33334d"
    READONLY_BG = "#2f2f47"

    parent.configure(bg=BG)

    # ---------------- MAIN SPLIT FRAME ----------------
    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    # ---------------- LEFT FRAME (Mark Attendance - 35%) ----------------
    left_frame = tk.Frame(main, bg=BG)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0,10))
    left_frame.columnconfigure(0, weight=1)

    # Form Card
    form_card = tk.Frame(left_frame, bg=CARD_BG, bd=0, highlightthickness=0, relief="ridge")
    form_card.pack(fill="both", pady=10, padx=0)

    tk.Label(form_card, text="Mark Member Attendance", bg=CARD_BG, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(20,10), padx=20)

    form_body = tk.Frame(form_card, bg=CARD_BG)
    form_body.pack(fill="both", expand=True, padx=20, pady=10)

    # Form fields
    tk.Label(form_body, text="Select Member:", bg=CARD_BG, fg=LABEL, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=12)
    member_cb = ttk.Combobox(form_body, width=25, font=("Segoe UI", 10))
    member_cb.grid(row=0, column=1, pady=12, padx=5)

    tk.Label(form_body, text="Date:", bg=CARD_BG, fg=LABEL, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=12)
    ent_date = tk.Entry(form_body, width=25, bg=READONLY_BG, fg=BG, font=("Segoe UI", 10), relief="flat", justify="left")
    ent_date.grid(row=1, column=1, pady=12, padx=5)
    ent_date.insert(0, datetime.today().strftime("%Y-%m-%d"))
    ent_date.config(state="readonly")

    # Buttons frame evenly spaced
    btn_frame = tk.Frame(form_body, bg=CARD_BG)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    btn_checkin = tk.Button(btn_frame, text="Mark Check-in", bg=ACCENT, fg=TEXT,
                            font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=6)
    btn_checkin.grid(row=0, column=0, sticky="ew", padx=(0,5))

    btn_checkout = tk.Button(btn_frame, text="Mark Check-out", bg=ACCENT, fg=TEXT,
                             font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=6)
    btn_checkout.grid(row=0, column=1, sticky="ew", padx=(5,0))

    # Mark All Present
    btn_mark_all = tk.Button(form_card, text="Mark All Present", bg=ACCENT, fg=TEXT,
                             font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=8)
    btn_mark_all.pack(fill="x", pady=(10,20), padx=20)

    # ---------------- RIGHT FRAME (Attendance History - 65%) ----------------
    right_frame = tk.Frame(main, bg=BG)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10,0))
    right_frame.columnconfigure(0, weight=1)

    # History Card
    history_card = tk.Frame(right_frame, bg=CARD_BG, bd=0, highlightthickness=0)
    history_card.pack(fill="both", expand=True, pady=10)

    tk.Label(history_card, text="Member Attendance History", bg=CARD_BG, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(20,10), padx=20)

    # ---------- Treeview Style ----------
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2a2a3f", foreground="#ffffff", rowheight=28, fieldbackground="#2a2a3f", borderwidth=0)
    style.configure("Treeview.Heading", background="#7c5dfa", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", "#7c5dfa")])

    history_tree = ttk.Treeview(history_card, columns=("date", "member", "checkin", "checkout"), show="headings", height=20)
    history_tree.heading("date", text="Date")
    history_tree.heading("member", text="Member Name")
    history_tree.heading("checkin", text="Check-in Time")
    history_tree.heading("checkout", text="Check-out Time")
    history_tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- DB FUNCTIONS ----------------
    def load_members():
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT member_id, name FROM members WHERE trainer_id=%s", (trainer_id,))
            members = cursor.fetchall()
            # Show names but keep IDs internally
            member_cb['values'] = [f"{m['member_id']} - {m['name']}" for m in members]
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_history():
        for row in history_tree.get_children():
            history_tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.date, m.name AS member_name, a.check_in, a.check_out
                FROM attendance a
                LEFT JOIN members m ON a.user_id = m.member_id
                WHERE m.trainer_id=%s
                ORDER BY a.date DESC, a.check_in DESC
            """, (trainer_id,))
            for row in cursor.fetchall():
                history_tree.insert("", tk.END, values=(row["date"], row["member_name"], row["check_in"], row["check_out"]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- BUTTON LOGIC ----------------
    def mark_checkin():
        member_val = member_cb.get()
        if not member_val:
            messagebox.showerror("Error", "Select a member")
            return
        member_id = member_val.split(" - ")[0]
        date_today = ent_date.get()
        time_now = datetime.now().strftime("%H:%M:%S")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM attendance WHERE user_id=%s AND date=%s", (member_id, date_today))
            existing = cursor.fetchone()
            if existing:
                messagebox.showerror("Error", "Member already checked in for today")
                return
            cursor.execute("INSERT INTO attendance (user_id, date, check_in) VALUES (%s, %s, %s)", (member_id, date_today, time_now))
            conn.commit()
            conn.close()
            refresh_history()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_checkout():
        member_val = member_cb.get()
        if not member_val:
            messagebox.showerror("Error", "Select a member")
            return
        member_id = member_val.split(" - ")[0]
        date_today = ent_date.get()
        time_now = datetime.now().strftime("%H:%M:%S")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM attendance WHERE user_id=%s AND date=%s", (member_id, date_today))
            existing = cursor.fetchone()
            if not existing:
                messagebox.showerror("Error", "Member has not checked in today")
                return
            cursor.execute("UPDATE attendance SET check_out=%s WHERE user_id=%s AND date=%s", (time_now, member_id, date_today))
            conn.commit()
            conn.close()
            refresh_history()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_all_present():
        date_today = ent_date.get()
        time_now = datetime.now().strftime("%H:%M:%S")
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT member_id FROM members WHERE trainer_id=%s", (trainer_id,))
            members = cursor.fetchall()
            for m in members:
                cursor.execute("SELECT * FROM attendance WHERE user_id=%s AND date=%s", (m['member_id'], date_today))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO attendance (user_id, date, check_in) VALUES (%s, %s, %s)", (m['member_id'], date_today, time_now))
            conn.commit()
            conn.close()
            refresh_history()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Bind buttons
    btn_checkin.config(command=mark_checkin)
    btn_checkout.config(command=mark_checkout)
    btn_mark_all.config(command=mark_all_present)

    # Initial load
    load_members()
    refresh_history()
