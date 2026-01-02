import tkinter as tk
from admin.manage_users import load_manage_users
from admin.manage_members import load_manage_members
from admin.manage_trainers import load_manage_trainers
from admin.manage_attendant import load_manage_attendants
from admin.manage_managers import load_manage_managers
from admin.manage_gym_branches import load_manage_gym_branches
from admin.manage_workout_zones import load_manage_workout_zones




def open_admin_dashboard():
    win = tk.Tk()
    win.title("Admin Dashboard - Smart Gym")
    win.geometry("1300x750")
    win.configure(bg="#1e1e2f")

    # ================= TOP BAR =================
    topbar = tk.Frame(win, bg="#252540", height=60)
    topbar.pack(fill="x")

    tk.Label(
        topbar,
        text="F9's Fitness",
        bg="#252540",
        fg="white",
        font=("Arial", 18, "bold")
    ).pack(side="left", padx=20)

    tk.Label(
        topbar,
        text="Role: ADMIN",
        bg="#252540",
        fg="#b3b3cc",
        font=("Arial", 11)
    ).pack(side="right", padx=20)

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

    def update_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    sidebar.bind("<Configure>", update_scroll)

    # -------- BUTTON HELPERS --------
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

    # -------- MENU ITEMS --------
    main_btn("Home").pack(fill="x")

    # ===== MANAGE PERSONS (SHOW ALL AS NORMAL BUTTONS) =====
    main_btn(
    "Manage Members",
    lambda: load_manage_members(content)
).pack(fill="x")
    main_btn(
    "Manage Trainers",
    lambda: load_manage_trainers(content)
).pack(fill="x")
    main_btn(
    "Manage Attendants",
    lambda: load_manage_attendants(content)
).pack(fill="x")
    main_btn(
    "Manage Managers",
    lambda: load_manage_managers(content)
).pack(fill="x")
    
    main_btn(
    "Manage Users",
    lambda: load_manage_users(content)
).pack(fill="x")

    # ===== OTHER MENUS =====
    main_btn(
    "Manage Gym Branches",
    lambda: load_manage_gym_branches(content)
).pack(fill="x")
    main_btn(
    "Manage Workout Zones",
    lambda: load_manage_workout_zones(content)
).pack(fill="x")
   
    main_btn("Attendance Tracking").pack(fill="x")
    main_btn("Manage Appointments").pack(fill="x")
    main_btn("Subscriptions").pack(fill="x")
    main_btn("Equipments").pack(fill="x")
    main_btn("Reports").pack(fill="x")
    main_btn("Salaries").pack(fill="x")
    main_btn("Payments").pack(fill="x")
    main_btn("Manage Announcements").pack(fill="x")
    main_btn("Trainer Schedules").pack(fill="x")
    main_btn("Logout").pack(fill="x")

    # ================= CONTENT AREA =================
    content = tk.Frame(body, bg="#1e1e2f")
    content.pack(fill="both", expand=True, padx=25, pady=20)

    tk.Label(
        content,
        text="Dashboard Overview",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", pady=(0, 20))

    cards_frame = tk.Frame(content, bg="#1e1e2f")
    cards_frame.pack(fill="x")

    stats = [
        ("Total Members", "120"),
        ("Active Trainers", "15"),
        ("Branches", "5"),
        ("Monthly Revenue", "PKR 350,000"),
        ("Pending Payments", "12")
    ]

    for i, (title, value) in enumerate(stats):
        card = tk.Frame(cards_frame, bg="#2f2f4f", width=220, height=110)
        card.grid(row=0, column=i, padx=10)
        card.grid_propagate(False)

        tk.Label(
            card,
            text=value,
            bg="#2f2f4f",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=(25, 5))

        tk.Label(
            card,
            text=title,
            bg="#2f2f4f",
            fg="#b3b3cc",
            font=("Arial", 10)
        ).pack()

    lower = tk.Frame(content, bg="#1e1e2f")
    lower.pack(fill="both", expand=True, pady=25)

    left_box = tk.Frame(lower, bg="#2f2f4f")
    left_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

    tk.Label(
        left_box,
        text="Revenue Reports (Graph)",
        bg="#2f2f4f",
        fg="white",
        font=("Arial", 14, "bold")
    ).pack(pady=20)

    right_box = tk.Frame(lower, bg="#2f2f4f")
    right_box.pack(side="left", fill="both", expand=True, padx=(10, 0))

    tk.Label(
        right_box,
        text="Recent Activities",
        bg="#2f2f4f",
        fg="white",
        font=("Arial", 14, "bold")
    ).pack(pady=20)

    win.mainloop()

# # Run the dashboard
# open_admin_dashboard()
