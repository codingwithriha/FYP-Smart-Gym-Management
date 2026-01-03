import tkinter as tk
from tkinter import messagebox
from database_db import get_connection
from member.home import load_member_home
from member.subscriptions import load_subscription_page
from member.appointments import load_appointments_page
from member.attendance import load_attendance_page
from member.announcements import load_announcements_page
from member.payments import load_payments_page
from member.workout_zones import load_workout_zones_page


# ================= GET MEMBER INFO =================
def get_member_info(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, email FROM users WHERE id = %s",
        (member_id,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0], result[1]
    return "Member", "member@email.com"


# ================= MEMBER DASHBOARD =================
def open_member_dashboard(member_id, username):
    win = tk.Tk()
    win.title("Member Dashboard - Smart Gym")
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

    # ================= MEMBER INFO =================
    username, email = get_member_info(member_id)

    # -------- PANEL TITLE --------
    tk.Label(
        sidebar,
        text="MEMBER",
        bg="#252540",
        fg="white",
        font=("Arial", 14, "bold")
    ).pack(pady=(18, 4))

    # -------- MEMBER NAME --------
    tk.Label(
        sidebar,
        text=username,
        bg="#252540",
        fg="#7c5dfa",
        font=("Arial", 12, "bold")
    ).pack(pady=(2, 1))

    # -------- MEMBER EMAIL --------
    tk.Label(
        sidebar,
        text=email,
        bg="#252540",
        fg="#b3b3cc",
        font=("Arial", 9)
    ).pack(pady=(0, 8))

    # -------- DIVIDER --------
    tk.Frame(
        sidebar,
        bg="#3a3a55",
        height=1
    ).pack(fill="x", padx=22, pady=6)

    # ================= BUTTON HELPER =================
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
            command=cmd
        )

    # ================= LOGOUT =================
    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            win.destroy()

    # ================= MENU =================
    menu_btn("Dashboard", lambda: load_member_home(content, username)).pack(fill="x")
    menu_btn("Subscription", lambda: load_subscription_page(content, member_id)).pack(fill="x")
    menu_btn("Appointments", lambda: load_appointments_page(content, member_id)).pack(fill="x")
    menu_btn("Attendance", lambda: load_attendance_page(content, member_id)).pack(fill="x")
    menu_btn("Announcements", lambda: load_announcements_page(content)).pack(fill="x")
    menu_btn("Payments", lambda: load_payments_page(content, member_id)).pack(fill="x")
    menu_btn("Trainer").pack(fill="x")
    menu_btn("Workout Zones", lambda: load_workout_zones_page(content)).pack(fill="x")
    menu_btn("Messages").pack(fill="x")
    menu_btn("Profile").pack(fill="x")
    menu_btn("Reset Password").pack(fill="x")
    menu_btn("Logout", logout).pack(fill="x", pady=(6, 0))

    # ================= DEFAULT PAGE =================
    load_member_home(content, username)

    win.mainloop()
