import tkinter as tk
from tkinter import messagebox
from manager.home import load_manager_home


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
    menu_btn("Members").pack(fill="x")
    menu_btn("Trainers").pack(fill="x")
    menu_btn("Gym Attendants").pack(fill="x")
    menu_btn("Attendance Tracking").pack(fill="x")
    menu_btn("Appointments").pack(fill="x")
    menu_btn("Subscriptions").pack(fill="x")
    menu_btn("Equipments").pack(fill="x")
    menu_btn("Reports").pack(fill="x")
    menu_btn("Payments").pack(fill="x")
    menu_btn("Announcements").pack(fill="x")
    menu_btn("Trainer Schedules").pack(fill="x")
    menu_btn("View Messages").pack(fill="x")
    menu_btn("Workout Zones").pack(fill="x")

    # -------- LOGOUT --------
    menu_btn("Logout", logout).pack(fill="x", pady=(6, 0))
    # ================= DEFAULT PAGE =================
    load_manager_home(content)
    
    win.mainloop()
    # DEFAULT PAGE (Auto-load Dashboard)


