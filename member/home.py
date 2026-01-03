import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def load_member_home(content, username="Test"):
    # Clear screen
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1f1b2e")

    # ================= HELLO TEXT =================
    tk.Label(
        content,
        text=f"Hello, {username}",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 2))

    tk.Label(
        content,
        text="Welcome to your fitness dashboard",
        bg="#1f1b2e",
        fg="#b8b6c9",
        font=("Segoe UI", 11)
    ).pack(anchor="w", padx=30, pady=(0, 15))

    # ================= INFO CARD =================
    info_card = tk.Frame(content, bg="#2a2440", height=70)
    info_card.pack(fill="x", padx=30)
    info_card.pack_propagate(False)

    tk.Label(
        info_card,
        text="🏋️ M9's Fitness  |  Gulberg, Lahore  |  455987",
        bg="#2a2440",
        fg="white",
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", padx=20, pady=12)

    tk.Label(
        info_card,
        text="🧘 Muscle Zone  |  Bodybuilding",
        bg="#2a2440",
        fg="#c7c5dd",
        font=("Segoe UI", 10)
    ).pack(anchor="w", padx=20)

    # ================= STATS CARDS =================
    cards_frame = tk.Frame(content, bg="#1f1b2e")
    cards_frame.pack(fill="x", padx=30, pady=20)

    def stat_card(parent, title, value):
        card = tk.Frame(parent, bg="#2a2440", width=250, height=80)
        card.pack(side="left", expand=True, padx=10)
        card.pack_propagate(False)

        tk.Label(
            card, text=value,
            bg="#2a2440", fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(15, 0))

        tk.Label(
            card, text=title,
            bg="#2a2440", fg="#b8b6c9",
            font=("Segoe UI", 10)
        ).pack()

    stat_card(cards_frame, "Active Subscriptions", "1")
    stat_card(cards_frame, "Upcoming Appointments", "0")
    stat_card(cards_frame, "This Month Attendance", "1")

    # ================= GRAPH CARD =================
    graph_card = tk.Frame(content, bg="#2a2440", height=320)
    graph_card.pack(fill="x", padx=30, pady=(0, 20))
    graph_card.pack_propagate(False)

    tk.Label(
        graph_card,
        text="Attendance - Last 7 Days",
        bg="#2a2440",
        fg="white",
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", padx=20, pady=10)

    # Graph data (later DB se replace hoga)
    days = ["Oct 08", "Oct 09", "Oct 10", "Oct 11", "Oct 12", "Oct 13", "Oct 14"]
    attendance = [0, 0, 0, 0, 0, 0, 0]

    fig = Figure(figsize=(9, 3), dpi=100)
    ax = fig.add_subplot(111)

    ax.plot(days, attendance, marker="o", linewidth=2)
    ax.set_facecolor("#2a2440")
    fig.patch.set_facecolor("#2a2440")

    ax.tick_params(colors="#c7c5dd")
    ax.spines["bottom"].set_color("#555")
    ax.spines["left"].set_color("#555")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.2)

    canvas = FigureCanvasTkAgg(fig, master=graph_card)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=10)
