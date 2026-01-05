import tkinter as tk
from tkinter import ttk
from database_db import get_connection
from datetime import datetime

# ================= COLORS =================
BG = "#1e1e2f"
CARD_BG = "#2a2a3d"
PRIMARY = "#7c5dfa"
TEXT = "#ffffff"
MUTED = "#b5b5d6"


def load_notifications(main_frame):
    """Load System Notifications Page"""

    # Clear previous widgets
    for widget in main_frame.winfo_children():
        widget.destroy()

    # ------------------ Main Frame ------------------
    main_frame = tk.Frame(main_frame, bg=BG)
    main_frame.pack(fill="both", expand=True)

    # ------------------ Top Bar ------------------
    top_bar = tk.Frame(main_frame, bg=PRIMARY, height=50)
    top_bar.pack(fill="x")
    tk.Label(top_bar, text="System Notifications", bg=PRIMARY, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(expand=True)

    # ------------------ Notifications Frame ------------------
    notif_frame = tk.Frame(main_frame, bg=BG)
    notif_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # Scrollbar
    canvas = tk.Canvas(notif_frame, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(notif_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG)

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

    # ------------------ Load Announcements from DB ------------------
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT title, message, created_at
        FROM announcements
        ORDER BY created_at DESC
    """)
    announcements = cursor.fetchall()
    conn.close()

    if not announcements:
        tk.Label(scrollable_frame, text="No notifications available.", bg=BG,
                 fg=MUTED, font=("Segoe UI", 12)).pack(pady=20)
        return

    # ------------------ Render Each Announcement ------------------
    for ann in announcements:
        card = tk.Frame(scrollable_frame, bg=CARD_BG, bd=1, relief="ridge", padx=12, pady=8)
        card.pack(fill="x", pady=8)

        # Title
        tk.Label(card, text=ann["title"], bg=CARD_BG, fg=PRIMARY,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")

        # Message
        tk.Label(card, text=ann["message"], bg=CARD_BG, fg=TEXT,
                 font=("Segoe UI", 11), wraplength=600, justify="left").pack(anchor="w", pady=(2,4))

        # Created At
        if ann["created_at"]:
            created_str = ann["created_at"].strftime("%Y-%m-%d %H:%M")
            tk.Label(card, text=f"Date: {created_str}", bg=CARD_BG, fg=MUTED,
                     font=("Segoe UI", 9, "italic")).pack(anchor="e")

