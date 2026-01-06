import tkinter as tk
from tkinter import ttk, messagebox
from database_db import get_connection

# ================= TRAINER SCHEDULE PAGE =================
def load_schedule(parent, trainer_id):

    # Clear page
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

    main.columnconfigure(0, weight=1)
    main.columnconfigure(1, weight=2)

    # =====================================================
    # LEFT SIDE → SET SCHEDULE
    # =====================================================
    left = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

    tk.Label(
        left,
        text="My Working Schedule",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 10))

    form = tk.Frame(left, bg=CARD)
    form.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------- Day ----------
    tk.Label(form, text="Day of Week", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=10)

    day_cb = ttk.Combobox(
        form,
        values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        state="readonly",
        width=22
    )
    day_cb.grid(row=0, column=1, pady=10)

    # ---------- Activity (DROPDOWN) ----------
    tk.Label(form, text="Activity", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)

    activity_cb = ttk.Combobox(
        form,
        state="readonly",
        width=22
    )
    activity_cb.grid(row=1, column=1, pady=10)

    # ---------- Start Time ----------
    tk.Label(form, text="Start Time (HH:MM)", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)

    start_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT, relief="flat", width=25)
    start_entry.grid(row=2, column=1, pady=10)

    # ---------- End Time ----------
    tk.Label(form, text="End Time (HH:MM)", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=10)

    end_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT, relief="flat", width=25)
    end_entry.grid(row=3, column=1, pady=10)

    # ---------- SAVE BUTTON ----------
    def save_schedule():
        day = day_cb.get()
        activity = activity_cb.get()
        start = start_entry.get()
        end = end_entry.get()

        if not day or not activity or not start or not end:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT schedule_id FROM schedules
                WHERE trainer_id=%s AND day_of_week=%s
            """, (trainer_id, day))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE schedules
                    SET activity=%s, start_time=%s, end_time=%s
                    WHERE trainer_id=%s AND day_of_week=%s
                """, (activity, start, end, trainer_id, day))
            else:
                cursor.execute("""
                    INSERT INTO schedules (trainer_id, day_of_week, activity, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, (trainer_id, day, activity, start, end))

            conn.commit()
            load_schedule_table()
            load_activities()
            messagebox.showinfo("Success", "Schedule saved successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(
        left,
        text="Save Schedule",
        bg=ACCENT,
        fg=TEXT,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        pady=8,
        command=save_schedule
    ).pack(fill="x", padx=20, pady=(10, 20))

    # =====================================================
    # RIGHT SIDE → VIEW SCHEDULE
    # =====================================================
    right = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    right.grid(row=0, column=1, sticky="nsew")

    tk.Label(
        right,
        text="Weekly Schedule Overview",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 10))

    # ---------- TREEVIEW STYLE ----------
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background=CARD,
        foreground=TEXT,
        rowheight=32,
        fieldbackground=CARD,
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background=ACCENT,
        foreground=TEXT,
        font=("Segoe UI", 10, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", ACCENT)]
    )

    columns = ("day", "activity", "start", "end")
    tree = ttk.Treeview(right, columns=columns, show="headings", height=12)

    for col, txt in zip(columns, ["Day", "Activity", "Start Time", "End Time"]):
        tree.heading(col, text=txt)
        tree.column(col, anchor="center", width=140)

    tree.pack(fill="both", expand=True, padx=20, pady=15)

    # ---------- LOAD FUNCTIONS ----------
    def load_activities():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT activity FROM schedules WHERE activity IS NOT NULL")
            activities = [row[0] for row in cursor.fetchall()]
            activity_cb["values"] = activities
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_schedule_table():
        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT day_of_week, activity, start_time, end_time
                FROM schedules
                WHERE trainer_id=%s
                ORDER BY FIELD(day_of_week,
                'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
            """, (trainer_id,))

            for row in cursor.fetchall():
                tree.insert("", "end", values=(
                    row["day_of_week"],
                    row["activity"],
                    row["start_time"],
                    row["end_time"]
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    load_activities()
    load_schedule_table()
