import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database_db import get_connection

# ✅ IMPORT REAL HOME DASHBOARD
from trainer.home import load_home
from trainer.members import load_members 
from trainer.attendance import load_attendance 
from trainer.chat import load_chat # <-- THIS FIXES EVERYTHING

# ================= COLORS =================
BG = "#1e1e2f"
SIDEBAR_BG = "#1b1b2f"
PRIMARY = "#7c5dfa"
TEXT = "#ffffff"
MUTED = "#b5b5d6"
BTN_HOVER = "#5a3fd8"

# ================= ICONS (Unicode) =================
ICONS = {
    "Home": "🏠",
    "My Members": "👥",
    "Attendance": "🗓️",
    "Chat": "💬",
    "Schedule / Activities": "⏰",
    "Appointments": "📅",
    "Performance Reports": "📊",
    "Reset Password": "🔒",
    "Profile": "👤",
    "Logout": "🚪"
}

def open_trainer_dashboard(trainer_id):
    """Launch the Trainer Dashboard with modern SaaS style UI"""

    # ------------------ Fetch Trainer ------------------
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT trainer_id, name FROM trainers WHERE trainer_id=%s",
        (trainer_id,)
    )
    trainer = cursor.fetchone()
    conn.close()

    if not trainer:
        messagebox.showerror("Error", "Trainer not found!")
        return

    # ================= MAIN WINDOW =================
    root = tk.Tk()
    root.title("Trainer Dashboard")
    root.geometry("1250x750")
    root.configure(bg=BG)

    # ------------------ Top Info Bar ------------------
    top_bar = tk.Frame(root, bg=PRIMARY, height=80, padx=40, pady=20)
    top_bar.pack(fill="x")

    tk.Label(
        top_bar,
        text=f"Welcome, {trainer['name']}",
        bg=PRIMARY,
        fg=TEXT,
        font=("Segoe UI", 16, "bold")
    ).pack(side="left", padx=(0, 40))

    tk.Label(
        top_bar,
        text=f"ID: {trainer['trainer_id']}",
        bg=PRIMARY,
        fg=TEXT,
        font=("Segoe UI", 13)
    ).pack(side="left")

    lbl_time = tk.Label(
        top_bar,
        bg=PRIMARY,
        fg=TEXT,
        font=("Segoe UI", 13)
    )
    lbl_time.pack(side="right", padx=40)

    def update_time():
        lbl_time.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        lbl_time.after(1000, update_time)

    update_time()

    # ------------------ Sidebar ------------------
    sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=270)
    sidebar.pack(side="left", fill="y")

    main_frame = tk.Frame(root, bg=BG)
    main_frame.pack(side="right", fill="both", expand=True)

    # ------------------ Hover Effects ------------------
    def on_enter(e):
        e.widget["bg"] = BTN_HOVER

    def on_leave(e):
        e.widget["bg"] = SIDEBAR_BG

    # ------------------ Logout Confirm ------------------
    def confirm_logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            root.destroy()

    # ------------------ Page Loader ------------------
    def load_page(name):
        pages = {
            "Home": load_home,
            "My Members": load_members,
            "Attendance": load_attendance,
            "Chat": load_chat,
            "Schedule / Activities": load_schedule,
            "Appointments": load_appointments,
            "Performance Reports": load_reports,
            "Reset Password": load_reset_password,
            "Profile": load_profile,
            "Logout": lambda f, t: confirm_logout()
        }
        pages[name](main_frame, trainer_id)

    # ------------------ Menu Buttons ------------------
    menu_buttons = [
        "Home",
        "My Members",
        "Attendance",
        "Chat",
        "Schedule / Activities",
        "Appointments",
        "Performance Reports",
        "Reset Password",
        "Profile",
        "Logout"
    ]

    for text in menu_buttons:
        btn = tk.Button(
            sidebar,
            text=f"{ICONS[text]}   {text}",
            bg=SIDEBAR_BG,
            fg=TEXT,
            font=("Segoe UI", 12),
            anchor="w",
            bd=0,
            relief="flat",
            padx=25,
            pady=12,
            command=lambda t=text: load_page(t)
        )
        btn.pack(fill="x", padx=12)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # ------------------ Load Default Home ------------------
    load_home(main_frame, trainer_id)

    root.mainloop()

# ================= Utility =================
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# ================= Placeholder Pages (INTACT) =================



def load_schedule(frame, trainer_id):
    clear_frame(frame)
    tk.Label(frame, text="⏰ Schedule / Activities", bg=BG, fg=TEXT,
             font=("Segoe UI", 20, "bold")).pack(pady=40)

def load_appointments(frame, trainer_id):
    clear_frame(frame)
    tk.Label(frame, text="📅 Appointments", bg=BG, fg=TEXT,
             font=("Segoe UI", 20, "bold")).pack(pady=40)

def load_reports(frame, trainer_id):
    clear_frame(frame)
    tk.Label(frame, text="📊 Performance Reports", bg=BG, fg=TEXT,
             font=("Segoe UI", 20, "bold")).pack(pady=40)

def load_reset_password(frame, trainer_id):
    clear_frame(frame)
    tk.Label(frame, text="🔒 Reset Password", bg=BG, fg=TEXT,
             font=("Segoe UI", 20, "bold")).pack(pady=40)

def load_profile(frame, trainer_id):
    clear_frame(frame)
    tk.Label(frame, text="👤 Profile", bg=BG, fg=TEXT,
             font=("Segoe UI", 20, "bold")).pack(pady=40)
