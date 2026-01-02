import tkinter as tk
from tkinter import ttk, messagebox
from admin.home import load_home
from admin.manage_users import load_manage_users
from admin.manage_members import load_manage_members
from admin.manage_trainers import load_manage_trainers
from admin.manage_attendant import load_manage_attendants
from admin.manage_managers import load_manage_managers
from admin.manage_gym_branches import load_manage_gym_branches
from admin.manage_workout_zones import load_manage_workout_zones
from admin.manage_attendance import load_manage_attendance
from admin.manage_appointments import load_manage_appointments
from admin.subscriptions import load_manage_subscriptions
from admin.reports import load_manage_reports
from admin.salaries import load_manage_salaries
from admin.payments import load_manage_payments
from admin.announcements import load_manage_announcements
from admin.trainer_schedule import load_manage_schedules
from admin.equipments import load_manage_equipment


def open_admin_dashboard():
    win = tk.Tk()
    win.title("Admin Dashboard - Smart Gym")
    win.geometry("1300x750")
    win.configure(bg="#1e1e2f")

    # ================= TOP BAR =================
    topbar = tk.Frame(win, bg="#252540", height=60)
    topbar.pack(fill="x")
    tk.Label(topbar, text="F9's Fitness", bg="#252540", fg="white",
             font=("Arial", 18, "bold")).pack(side="left", padx=20)
    tk.Label(topbar, text="Role: ADMIN", bg="#252540", fg="#b3b3cc",
             font=("Arial", 11)).pack(side="right", padx=20)

    # ================= MAIN BODY =================
    body = tk.Frame(win, bg="#1e1e2f")
    body.pack(fill="both", expand=True)

    # ================= SIDEBAR (SCROLLABLE) =================
    sidebar_container = tk.Frame(body, bg="#252540", width=230)
    sidebar_container.pack(side="left", fill="y")
    sidebar_container.pack_propagate(False)

    canvas = tk.Canvas(sidebar_container, bg="#252540", highlightthickness=0)
    scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    sidebar = tk.Frame(canvas, bg="#252540")
    canvas.create_window((0, 0), window=sidebar, anchor="nw")
    sidebar.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # ================= CONTENT AREA =================
    content = tk.Frame(body, bg="#1e1e2f")
    content.pack(fill="both", expand=True, padx=25, pady=20)

    # -------- BUTTON HELPER --------
    def main_btn(text, cmd=None):
        return tk.Button(
            sidebar, text=text,
            bg="#252540", fg="white",
            bd=0, anchor="w",
            font=("Arial", 11, "bold"),
            padx=25, pady=12,
            activebackground="#7c5dfa",
            activeforeground="white",
            command=cmd
        )

    # -------- LOGOUT FUNCTION WITH CONFIRMATION --------
    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            win.destroy()

    # -------- MENU ITEMS --------
    main_btn("Home", lambda: load_home(content)).pack(fill="x")
    main_btn("Manage Members", lambda: load_manage_members(content)).pack(fill="x")
    main_btn("Manage Trainers", lambda: load_manage_trainers(content)).pack(fill="x")
    main_btn("Manage Attendants", lambda: load_manage_attendants(content)).pack(fill="x")
    main_btn("Manage Managers", lambda: load_manage_managers(content)).pack(fill="x")
    main_btn("Manage Users", lambda: load_manage_users(content)).pack(fill="x")
    main_btn("Manage Gym Branches", lambda: load_manage_gym_branches(content)).pack(fill="x")
    main_btn("Manage Workout Zones", lambda: load_manage_workout_zones(content)).pack(fill="x")
    main_btn("Attendance Tracking", lambda: load_manage_attendance(content)).pack(fill="x")
    main_btn("Manage Appointments", lambda: load_manage_appointments(content)).pack(fill="x")
    main_btn("Subscriptions", lambda: load_manage_subscriptions(content)).pack(fill="x")
    main_btn("Equipments", lambda: load_manage_equipment(content)).pack(fill="x")
    main_btn("Reports", lambda: load_manage_reports(content)).pack(fill="x")
    main_btn("Salaries", lambda: load_manage_salaries(content)).pack(fill="x")
    main_btn("Payments", lambda: load_manage_payments(content)).pack(fill="x")
    main_btn("Manage Announcements", lambda: load_manage_announcements(content)).pack(fill="x")
    main_btn("Trainer Schedules", lambda: load_manage_schedules(content)).pack(fill="x")
    main_btn("Logout", logout).pack(fill="x")  # ✅ Logout with popup

    # Load Home by default
    load_home(content)

    win.mainloop()


# Uncomment to run
# open_admin_dashboard()
