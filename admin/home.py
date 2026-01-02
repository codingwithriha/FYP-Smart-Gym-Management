import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from database_db import get_connection
import random
import datetime

def load_home(content):
    # ================= CLEAR CONTENT =================
    for widget in content.winfo_children():
        widget.destroy()

    # ================= SCROLLABLE FRAME =================
    canvas = tk.Canvas(content, bg="#1e1e2f", highlightthickness=0)
    scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1e1e2f")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ================= ORIGINAL CONTENT STARTS =================
    tk.Label(
        scrollable_frame,
        text="Dashboard Overview",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 22, "bold")
    ).pack(anchor="w", pady=(0, 20))

    # ================= CARDS =================
    cards_frame = tk.Frame(scrollable_frame, bg="#1e1e2f")
    cards_frame.pack(fill="x", pady=(0,20))

    # -------- Get Data from DB --------
    conn = get_connection()
    cur = conn.cursor()

    # Total Members
    cur.execute("SELECT COUNT(*) FROM members")
    total_members = cur.fetchone()[0]

    # Active Trainers
    cur.execute("SELECT COUNT(*) FROM trainers")
    total_trainers = cur.fetchone()[0]

    # Branches
    cur.execute("SELECT COUNT(*) FROM branches")
    total_branches = cur.fetchone()[0]

    # Monthly Revenue (last month)
    cur.execute("SELECT SUM(amount) FROM payments WHERE MONTH(payment_date)=MONTH(CURDATE())")
    monthly_revenue = cur.fetchone()[0] or 0

    # Pending Payments
    cur.execute("SELECT COUNT(*) FROM payments WHERE status='Pending'")
    pending_payments = cur.fetchone()[0]

    conn.close()

    stats = [
        ("Total Members", total_members, "#4CAF50"),
        ("Active Trainers", total_trainers, "#2196F3"),
        ("Branches", total_branches, "#FF9800"),
        ("Monthly Revenue", f"PKR {monthly_revenue:,}", "#9C27B0"),
        ("Pending Payments", pending_payments, "#F44336")
    ]

    for i, (title, value, color) in enumerate(stats):
        card = tk.Frame(cards_frame, bg=color, width=220, height=110)
        card.grid(row=0, column=i, padx=10)
        card.grid_propagate(False)

        tk.Label(
            card,
            text=value,
            bg=color,
            fg="white",
            font=("Arial", 18, "bold")
        ).pack(pady=(25,5))

        tk.Label(
            card,
            text=title,
            bg=color,
            fg="white",
            font=("Arial", 11)
        ).pack()

    # ================= CHARTS =================
    charts_frame = tk.Frame(scrollable_frame, bg="#1e1e2f")
    charts_frame.pack(fill="both", expand=True)

    # ---------- Monthly Revenue Trend (Line Chart) ----------
    left_chart = tk.Frame(charts_frame, bg="#2f2f4f")
    left_chart.pack(side="left", fill="both", expand=True, padx=(0,5), pady=5)

    tk.Label(left_chart, text="Monthly Revenue Trend", bg="#2f2f4f", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

    # Dummy monthly revenue data
    months = [datetime.date(2026, m, 1).strftime('%b') for m in range(1,13)]
    revenue_data = [random.randint(20000, 50000) for _ in range(12)]

    fig1 = Figure(figsize=(5,3), dpi=100)
    ax1 = fig1.add_subplot(111)
    ax1.plot(months, revenue_data, marker='o', color="#4CAF50")
    ax1.set_ylabel("PKR")
    ax1.set_xlabel("Month")
    ax1.set_facecolor("#2f2f4f")
    fig1.patch.set_facecolor("#2f2f4f")
    ax1.tick_params(colors='white')
    ax1.spines['bottom'].set_color('white')
    ax1.spines['left'].set_color('white')
    ax1.spines['top'].set_color('white')
    ax1.spines['right'].set_color('white')
    ax1.yaxis.label.set_color('white')
    ax1.xaxis.label.set_color('white')

    canvas1 = FigureCanvasTkAgg(fig1, master=left_chart)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill="both", expand=True)

    # ---------- Payment Status Pie Chart ----------
    right_chart = tk.Frame(charts_frame, bg="#2f2f4f")
    right_chart.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)

    tk.Label(right_chart, text="Payments Status", bg="#2f2f4f", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

    # Dummy payment status
    payment_status = ["Paid", "Unpaid", "Pending"]
    payment_count = [random.randint(5,50) for _ in range(3)]
    colors = ["#4CAF50", "#F44336", "#FF9800"]

    fig2 = Figure(figsize=(5,3), dpi=100)
    ax2 = fig2.add_subplot(111)
    ax2.pie(payment_count, labels=payment_status, autopct='%1.1f%%', colors=colors, textprops={'color':'white'})
    fig2.patch.set_facecolor("#2f2f4f")

    canvas2 = FigureCanvasTkAgg(fig2, master=right_chart)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill="both", expand=True)

    # ================= SECOND ROW CHARTS =================
    charts_frame2 = tk.Frame(scrollable_frame, bg="#1e1e2f")
    charts_frame2.pack(fill="both", expand=True)

    # ---------- Weekly Attendance ----------
    left_chart2 = tk.Frame(charts_frame2, bg="#2f2f4f")
    left_chart2.pack(side="left", fill="both", expand=True, padx=(0,5), pady=5)

    tk.Label(left_chart2, text="Weekly Attendance", bg="#2f2f4f", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

    weekdays = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    attendance_data = [random.randint(5,20) for _ in range(7)]

    fig3 = Figure(figsize=(5,3), dpi=100)
    ax3 = fig3.add_subplot(111)
    ax3.bar(weekdays, attendance_data, color="#2196F3")
    ax3.set_ylabel("Members")
    ax3.set_xlabel("Day")
    ax3.set_facecolor("#2f2f4f")
    fig3.patch.set_facecolor("#2f2f4f")
    ax3.tick_params(colors='white')
    ax3.spines['bottom'].set_color('white')
    ax3.spines['left'].set_color('white')
    ax3.spines['top'].set_color('white')
    ax3.spines['right'].set_color('white')
    ax3.yaxis.label.set_color('white')
    ax3.xaxis.label.set_color('white')

    canvas3 = FigureCanvasTkAgg(fig3, master=left_chart2)
    canvas3.draw()
    canvas3.get_tk_widget().pack(fill="both", expand=True)

    # ---------- Equipment Status (Placeholder) ----------
    right_chart2 = tk.Frame(charts_frame2, bg="#2f2f4f")
    right_chart2.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)

    tk.Label(right_chart2, text="Equipment Status", bg="#2f2f4f", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

    equipment_labels = ["Treadmill","Cycle","Bench","Dumbbell","Row Machine"]
    equipment_data = [random.randint(0,5) for _ in range(5)]

    fig4 = Figure(figsize=(5,3), dpi=100)
    ax4 = fig4.add_subplot(111)
    ax4.bar(equipment_labels, equipment_data, color="#FF9800")
    ax4.set_ylabel("Available")
    ax4.set_xlabel("Equipment")
    ax4.set_facecolor("#2f2f4f")
    fig4.patch.set_facecolor("#2f2f4f")
    ax4.tick_params(colors='white')
    ax4.spines['bottom'].set_color('white')
    ax4.spines['left'].set_color('white')
    ax4.spines['top'].set_color('white')
    ax4.spines['right'].set_color('white')
    ax4.yaxis.label.set_color('white')
    ax4.xaxis.label.set_color('white')

    canvas4 = FigureCanvasTkAgg(fig4, master=right_chart2)
    canvas4.draw()
    canvas4.get_tk_widget().pack(fill="both", expand=True)
