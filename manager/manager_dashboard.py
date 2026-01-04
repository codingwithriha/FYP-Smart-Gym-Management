import tkinter as tk
from tkinter import messagebox
from manager.home import load_manager_home
from manager.members import load_manage_members
from manager.trainers import load_manage_trainers
from manager.attendants import load_manage_attendants
from manager.attendance import load_manage_attendance
from manager.appointments import load_manage_appointments
from manager.subscriptions import load_manage_subscriptions
from manager.equipments import load_manage_equipments
from manager.reports import load_manage_reports
from manager.payments import load_manage_payments
from manager.announcements import load_manage_announcements
from manager.trainer_schedules import load_manage_schedules
from manager.view_messages import load_manage_messages
from manager.workout_zones import load_manage_workout_zones


# ================= MANAGER DASHBOARD =================
def open_manager_dashboard(manager_name="Manager"):
    win = tk.Tk()
    win.title("Manager Dashboard - Smart Gym")
    win.geometry("1300x750")
    win.configure(bg="#1e1e2f")

    # ================= BODY =================
    body = tk.Frame(win, bg="#1e1e2f")
    body.pack(fill="both", expand=True)

    # ================= SIDEBAR =================
    sidebar = tk.Frame(body, bg="#252540", width=250)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # ================= CONTENT =================
    content = tk.Frame(body, bg="#1e1e2f")
    content.pack(fill="both", expand=True, padx=25, pady=20)

    # ================= BRANDING =================
    tk.Label(
        sidebar,
        text="F9's Fitness",
        bg="#252540",
        fg="white",
        font=("Arial", 15, "bold")
    ).pack(pady=(18, 2))

    tk.Label(
        sidebar,
        text="Manager Portal",
        bg="#252540",
        fg="#b3b3cc",
        font=("Arial", 10)
    ).pack(pady=(0, 10))

    # -------- DIVIDER --------
    tk.Frame(
        sidebar,
        bg="#3a3a55",
        height=1
    ).pack(fill="x", padx=22, pady=8)

    # ================= MENU BUTTON HELPER =================
    def menu_btn(text, cmd=None):
        return tk.Button(
            sidebar,
            text=text,
            bg="#252540",
            fg="white",
            bd=0,
            anchor="w",
            font=("Arial", 10),
            padx=28,
            pady=9,
            activebackground="#7c5dfa",
            activeforeground="white",
            cursor="hand2",
            command=cmd
        )

    # ================= LOGOUT =================
    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            win.destroy()

    # ================= MENU =================
    menu_btn("Dashboard", lambda: load_manager_home(content)).pack(fill="x")
    menu_btn("Members", lambda: load_manage_members(content)).pack(fill="x")
    menu_btn("Trainers", lambda: load_manage_trainers(content)).pack(fill="x")
    menu_btn("Gym Attendants", lambda: load_manage_attendants(content)).pack(fill="x")
    menu_btn("Attendance Tracking", lambda: load_manage_attendance(content)).pack(fill="x")
    menu_btn("Appointments", lambda: load_manage_appointments(content)).pack(fill="x")
    menu_btn("Subscriptions", lambda: load_manage_subscriptions(content)).pack(fill="x")
    menu_btn("Equipments", lambda: load_manage_equipments(content)).pack(fill="x")
    menu_btn("Reports", lambda: load_manage_reports(content)).pack(fill="x")
    menu_btn("Payments", lambda: load_manage_payments(content)).pack(fill="x")
    menu_btn("Announcements", lambda: load_manage_announcements(content)).pack(fill="x")
    menu_btn("Trainer Schedules", lambda: load_manage_schedules(content)).pack(fill="x")
    menu_btn("View Messages", lambda: load_manage_messages(content)).pack(fill="x")
    menu_btn("Workout Zones", lambda: load_manage_workout_zones(content)).pack(fill="x")

    # -------- LOGOUT --------
    menu_btn("Logout", logout).pack(fill="x", pady=(6, 0))
    # ================= DEFAULT PAGE =================
    load_manager_home(content)

    win.mainloop()
    # DEFAULT PAGE (Auto-load Dashboard)


