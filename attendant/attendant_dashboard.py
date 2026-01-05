import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from database_db import get_connection
from attendant.home import load_home
from attendant.profile import load_attendant_profile
from attendant.member_attendance import load_member_attendance
from attendant.trainer_attendance import load_trainer_attendance
from attendant.zone_members import load_zone_members
from attendant.zone_trainers import load_zone_trainers


# ================= COLORS =================
BG = "#1e1e2f"
TOP = "#7c5dfa"
MENU = "#2a2a3d"
TEXT = "#ffffff"

# ================= DASHBOARD =================
def open_attendant_dashboard(attendant_id):

    root = tk.Tk()
    root.title("Attendant Dashboard")
    root.geometry("1400x800")
    root.configure(bg=BG)

    # -------- FETCH ATTENDANT FROM DB --------
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT attendant_id, name FROM attendants WHERE attendant_id=%s",
            (attendant_id,)
        )
        attendant = cursor.fetchone()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        root.destroy()
        return

    if not attendant:
        messagebox.showerror("Error", "Attendant not found")
        root.destroy()
        return

    name = attendant["name"]

    # ================= TOP INFO BAR =================
    top_bar = tk.Frame(root, bg=TOP, height=80)
    top_bar.pack(side="top", fill="x")

    # Left info (Name + ID)
    info_frame = tk.Frame(top_bar, bg=TOP)
    info_frame.pack(side="left", padx=20, pady=15)

    tk.Label(
        info_frame,
        text=f"Welcome, {name}",
        bg=TOP, fg=TEXT,
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w")

    tk.Label(
        info_frame,
        text=f"Attendant ID: {attendant_id}",
        bg=TOP, fg=TEXT,
        font=("Segoe UI", 12)
    ).pack(anchor="w")

    # Right side (Clock + Logout)
    right_frame = tk.Frame(top_bar, bg=TOP)
    right_frame.pack(side="right", padx=20, pady=15)

    lbl_time = tk.Label(
        right_frame,
        bg=TOP, fg=TEXT,
        font=("Segoe UI", 12)
    )
    lbl_time.pack(side="left", padx=15)

    def update_time():
        lbl_time.config(
            text=datetime.now().strftime("%d %b %Y | %I:%M:%S %p")
        )
        lbl_time.after(1000, update_time)

    update_time()

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            root.destroy()

    tk.Button(
        right_frame,
        text="Logout",
        command=logout,
        bg="white",
        fg=TOP,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=10,
        pady=3
    ).pack(side="left", padx=10)

    # ================= MENU BUTTON FRAME =================
    menu_frame = tk.Frame(root, bg=MENU, height=50, bd=1, relief="raised")
    menu_frame.pack(side="top", fill="x", padx=20, pady=(10,0))

    # ================= MAIN CONTENT FRAME =================
    main_frame = tk.Frame(root, bg=BG)
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    menu_items = [
    ("Dashboard", lambda: load_home(main_frame, attendant_id)),
    ("Profile", lambda: load_attendant_profile(main_frame, attendant_id)),
    ("Member Attendance", lambda: load_member_attendance(main_frame)),
    ("Trainer Attendance", lambda: load_trainer_attendance(main_frame)),
    ("Zone Members", lambda: load_zone_members(main_frame, attendant_id)),
    ("Zone Trainers", lambda: load_zone_trainers(main_frame, attendant_id)),
    ("Equipment", None),
    ("Notifications", None),
    ("Reports", None)
]
    for text, cmd in menu_items:
        tk.Button(
        menu_frame,
        text=text,
        bg=MENU,
        fg=TEXT,
        relief="flat",
        font=("Segoe UI", 11),
        activebackground=TOP,
        activeforeground="white",
        padx=12,
        pady=5,
        command=cmd  # will be None if no function
    ).pack(side="left", padx=8, pady=5)


        

        # Initial load of home/dashboard
        load_home(main_frame, attendant_id)


    root.mainloop()
