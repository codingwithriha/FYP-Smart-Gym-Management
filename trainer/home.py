import tkinter as tk
from datetime import date, timedelta
from database_db import get_connection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ================= COLORS =================
BG = "#1e1e2f"
CARD_BG = "#7c5dfa"
CARD_HOVER = "#5a3fd8"
TEXT = "#ffffff"
MUTED = "#b5b5d6"
CHART_BG = "#2a2a3d"

# ================= UTILS =================
def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()

# ================= DASHBOARD =================
def load_home(frame, trainer_id):
    clear_frame(frame)

    # ---------- DB ----------
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    today = date.today()

    # Summary data
    cur.execute("SELECT COUNT(*) total FROM members WHERE trainer_id=%s", (trainer_id,))
    total_members = cur.fetchone()["total"]

    cur.execute("""
        SELECT COUNT(*) present
        FROM attendance a
        JOIN members m ON a.user_id=m.member_id
        WHERE a.date=%s AND a.status='Present' AND m.trainer_id=%s
    """, (today, trainer_id))
    present_today = cur.fetchone()["present"]

    cur.execute("""
        SELECT COUNT(*) total
        FROM appointments
        WHERE trainer_id=%s AND appointment_date=%s
    """, (trainer_id, today))
    appointments_today = cur.fetchone()["total"]

    attendance_rate = int((present_today / total_members) * 100) if total_members else 0

    # ================= SUMMARY CARDS =================
    cards_frame = tk.Frame(frame, bg=BG)
    cards_frame.pack(fill="x", padx=20, pady=15)

    cards = [
        ("👥 Total Members", total_members),
        ("🗓️ Present Today", present_today),
        ("📅 Appointments Today", appointments_today),
        ("📊 Attendance Rate", f"{attendance_rate}%")
    ]

    for i, (title, value) in enumerate(cards):
        card = tk.Frame(cards_frame, bg=CARD_BG, height=110)
        card.grid(row=0, column=i, sticky="nsew", padx=8)
        cards_frame.columnconfigure(i, weight=1)

        tk.Label(card, text=title, bg=CARD_BG, fg=MUTED,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        tk.Label(card, text=value, bg=CARD_BG, fg=TEXT,
                 font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=15)

    # ================= CHARTS =================
    charts = tk.Frame(frame, bg=BG)
    charts.pack(fill="both", expand=True, padx=20, pady=10)

    left = tk.Frame(charts, bg=BG)
    left.pack(side="left", fill="both", expand=True, padx=10)

    right = tk.Frame(charts, bg=BG)
    right.pack(side="right", fill="both", expand=True, padx=10)

    # ---------- LINE CHART (Attendance Over Last 7 Days) ----------
    start = today - timedelta(days=7)
    cur.execute("""
        SELECT a.date, COUNT(*) cnt
        FROM attendance a
        JOIN members m ON a.user_id=m.member_id
        WHERE m.trainer_id=%s AND a.date>= %s AND a.status='Present'
        GROUP BY a.date
        ORDER BY a.date
    """, (trainer_id, start))
    rows = cur.fetchall()
    dates = [r["date"].strftime("%d %b") for r in rows]
    counts = [r["cnt"] for r in rows]

    left_card1 = tk.Frame(left, bg=CHART_BG, padx=10, pady=10)
    left_card1.pack(fill="both", expand=True, pady=10)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(dates, counts, marker="o", linewidth=2, color="#5a3fd8")
    ax.set_title("Attendance Over Last 7 Days", color=TEXT, pad=15)
    ax.set_facecolor(CHART_BG)
    fig.patch.set_facecolor(CHART_BG)
    ax.tick_params(colors=TEXT)
    ax.set_xlabel("Date", color=TEXT)
    ax.set_ylabel("Present Members", color=TEXT)
    FigureCanvasTkAgg(fig, left_card1).get_tk_widget().pack(fill="both", expand=True)

    # ---------- PIE CHART (Today's Attendance) ----------
    absent = max(total_members - present_today, 0)
    left_card2 = tk.Frame(left, bg=CHART_BG, padx=10, pady=10)
    left_card2.pack(fill="both", expand=True, pady=10)
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    ax2.pie([present_today, absent],
            labels=["Present", "Absent"],
            autopct="%1.0f%%",
            startangle=90,
            colors=["#5a3fd8", "#b5b5d6"],
            textprops={"color": TEXT, "fontsize": 11})
    ax2.set_title("Today's Attendance", color=TEXT, pad=15)
    fig2.patch.set_facecolor(CHART_BG)
    FigureCanvasTkAgg(fig2, left_card2).get_tk_widget().pack(fill="both", expand=True)

    # ---------- BAR CHART (Appointments per Member) ----------
    cur.execute("""
        SELECT m.name, COUNT(a.appointment_id) total
        FROM members m
        LEFT JOIN appointments a ON m.member_id=a.member_id
        WHERE m.trainer_id=%s
        GROUP BY m.member_id
    """, (trainer_id,))
    data = cur.fetchall()
    names = [d["name"] for d in data]
    totals = [d["total"] for d in data]

    right_card1 = tk.Frame(right, bg=CHART_BG, padx=10, pady=10)
    right_card1.pack(fill="both", expand=True, pady=10)
    fig3, ax3 = plt.subplots(figsize=(5, 3))
    ax3.bar(names, totals, color="#7c5dfa")
    ax3.set_title("Appointments per Member", color=TEXT, pad=15)
    ax3.set_facecolor(CHART_BG)
    fig3.patch.set_facecolor(CHART_BG)
    ax3.tick_params(colors=TEXT)
    FigureCanvasTkAgg(fig3, right_card1).get_tk_widget().pack(fill="both", expand=True)

    # ---------- PIE CHART (Membership Distribution) ----------
    cur.execute("""
        SELECT membership_type, COUNT(*) total
        FROM members
        WHERE trainer_id=%s
        GROUP BY membership_type
    """, (trainer_id,))
    types = cur.fetchall()
    labels = [t["membership_type"] for t in types]
    values = [t["total"] for t in types]

    right_card2 = tk.Frame(right, bg=CHART_BG, padx=10, pady=10)
    right_card2.pack(fill="both", expand=True, pady=10)
    fig4, ax4 = plt.subplots(figsize=(5, 3))
    ax4.pie(values, labels=labels, autopct="%1.0f%%", startangle=90,
            textprops={"color": TEXT, "fontsize": 10},
            colors=["#7c5dfa","#5a3fd8","#b5b5d6"])
    ax4.set_title("Membership Distribution", color=TEXT, pad=15)
    fig4.patch.set_facecolor(CHART_BG)
    FigureCanvasTkAgg(fig4, right_card2).get_tk_widget().pack(fill="both", expand=True)

    conn.close()
