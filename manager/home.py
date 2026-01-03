import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database_db import get_connection
from datetime import date

# ================= MANAGER HOME =================
def load_manager_home(parent):

    # -------- Clear previous content --------
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg="#1e1e2f")

    # ================= HEADER =================
    header = tk.Frame(parent, bg="#1e1e2f")
    header.pack(fill="x", pady=(0, 15))

    tk.Label(
        header,
        text="Manager Dashboard",
        font=("Arial", 22, "bold"),
        fg="white",
        bg="#1e1e2f"
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Real-time insights for optimal gym performance",
        font=("Arial", 10),
        fg="#8f8fb3",
        bg="#1e1e2f"
    ).pack(anchor="w", pady=(2, 0))

    # ================= STAT CARDS =================
    cards_frame = tk.Frame(parent, bg="#1e1e2f")
    cards_frame.pack(fill="x", pady=15)

    def stat_card(title, value, color):
        card = tk.Frame(cards_frame, bg=color, width=150, height=90)  # reduced width
        card.pack(side="left", padx=8)
        card.pack_propagate(False)

        tk.Label(card, text=title, bg=color, fg="white",
                 font=("Arial", 9)).pack(anchor="w", padx=10, pady=(12, 0))

        tk.Label(card, text=value, bg=color, fg="white",
                 font=("Arial", 16, "bold")).pack(anchor="w", padx=10)

    # -------- Fetch data from database --------
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Total Members
        cursor.execute("SELECT COUNT(member_id) FROM members")
        total_members = cursor.fetchone()[0]

        # Active Today (attendance with today's date)
        today = date.today()
        cursor.execute("SELECT COUNT(user_id) FROM attendance WHERE date=%s", (today,))
        active_today = cursor.fetchone()[0]

        # Monthly Revenue (current month)
        cursor.execute("SELECT SUM(amount) FROM payments WHERE MONTH(payment_date)=MONTH(CURDATE()) AND YEAR(payment_date)=YEAR(CURDATE())")
        monthly_revenue = cursor.fetchone()[0] or 0
        monthly_revenue = f"${monthly_revenue:,}"

        # Pending Appointments
        cursor.execute("SELECT COUNT(appointment_id) FROM appointments WHERE status='pending'")
        pending_appointments = cursor.fetchone()[0]

        # Available Trainers
        cursor.execute("SELECT COUNT(trainer_id) FROM trainers WHERE status='available'")
        available_trainers = cursor.fetchone()[0]

        # Equipment Issues
        cursor.execute("SELECT COUNT(equipment_id) FROM equipment WHERE status='pending'")
        equipment_issues = cursor.fetchone()[0]

        cursor.close()
        conn.close()

    except Exception as e:
        total_members = active_today = monthly_revenue = pending_appointments = available_trainers = equipment_issues = "N/A"
        print("Error fetching dashboard data:", e)

    # -------- Create Cards --------
    stat_card("Total Members", total_members, "#6c5ce7")
    stat_card("Active Today", active_today, "#00b894")
    stat_card("Monthly Revenue", monthly_revenue, "#0984e3")
    stat_card("Pending Appointments", pending_appointments, "#fdcb6e")
    stat_card("Available Trainers", available_trainers, "#a29bfe")
    stat_card("Equipment Issues", equipment_issues, "#d63031")

    # ================= SCROLLABLE GRAPHS SECTION =================
    canvas = tk.Canvas(parent, bg="#1e1e2f", highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1e1e2f")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # -------- Graphs --------
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Attendance trend (last 12 days)
        cursor.execute("SELECT date, COUNT(user_id) FROM attendance GROUP BY date ORDER BY date DESC LIMIT 12")
        result = cursor.fetchall()
        result = sorted(result)  # chronological order
        attendance_dates = [str(r[0]) for r in result]
        attendance_counts = [r[1] for r in result]

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error fetching attendance trend:", e)
        attendance_dates = [f"Day {i}" for i in range(1, 13)]
        attendance_counts = [20, 25, 22, 28, 30, 29, 32, 31, 27, 30, 25, 15]

    # -------- Live Attendance Trend --------
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    fig1.patch.set_facecolor('#1e1e2f')
    ax1.set_facecolor('#1e1e2f')
    ax1.plot(attendance_dates, attendance_counts, color="#00b894", linewidth=2)
    ax1.set_title("Live Attendance Trend", color="white")
    ax1.set_ylabel("Attendance", color="white")
    ax1.set_xlabel("Date", color="white")
    ax1.tick_params(colors='white')
    ax1.grid(True, linestyle='--', alpha=0.5)

    canvas1 = FigureCanvasTkAgg(fig1, master=scrollable_frame)
    canvas1.draw()
    canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

    # -------- Membership Growth (static) --------
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    fig2.patch.set_facecolor('#1e1e2f')
    ax2.set_facecolor('#1e1e2f')
    months = ["Jan", "Feb"]
    members = [50, 75]
    ax2.bar(months, members, color="#0984e3")
    ax2.set_title("Membership Growth", color="white")
    ax2.set_ylabel("Members", color="white")
    ax2.tick_params(colors='white')

    canvas2 = FigureCanvasTkAgg(fig2, master=scrollable_frame)
    canvas2.draw()
    canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)

    # -------- Overall Performance Metrics (static) --------
    fig3, ax3 = plt.subplots(figsize=(5, 3))
    fig3.patch.set_facecolor('#1e1e2f')
    ax3.set_facecolor('#1e1e2f')
    metrics = ["Efficiency", "Satisfaction", "Capacity", "Usage"]
    values = [67, 73, 85, 80]
    ax3.barh(metrics, values, color="#6c5ce7")
    ax3.set_title("Overall Performance Metrics", color="white")
    ax3.set_xlim(0, 100)
    ax3.tick_params(colors='white')

    canvas3 = FigureCanvasTkAgg(fig3, master=scrollable_frame)
    canvas3.draw()
    canvas3.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

    # -------- Activity Distribution (static) --------
    fig4, ax4 = plt.subplots(figsize=(5, 3))
    fig4.patch.set_facecolor('#1e1e2f')
    ax4.set_facecolor('#1e1e2f')
    activities = ["Cardio", "Strength", "Yoga", "Classes", "Pool"]
    distribution = [17.2, 16.4, 19.1, 22.9, 24.3]
    ax4.pie(distribution, labels=activities, autopct="%1.1f%%", textprops={'color':'white'})
    ax4.set_title("Activity Distribution", color="white")

    canvas4 = FigureCanvasTkAgg(fig4, master=scrollable_frame)
    canvas4.draw()
    canvas4.get_tk_widget().grid(row=1, column=1, padx=10, pady=10)
