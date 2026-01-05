import tkinter as tk
from tkinter import messagebox
from database_db import get_connection

# ----------------- Login Function ----------------- #
def login():
    username_input = entry_username.get()
    password = entry_password.get()

    if username_input.strip() == "" or password.strip() == "":
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Fetch id, username, and role
        query = """
            SELECT id, username, role FROM users
            WHERE username=%s AND password=%s
        """
        cursor.execute(query, (username_input, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            user_id = user['id']
            username = user['username']
            role = user['role']

            root.destroy()  # Close login window

            # ----------------- Redirect based on role ----------------- #
            if role.lower() == "admin":
                import admin.admin_dashboard as admin_dashboard
                admin_dashboard.open_admin_dashboard()

            elif role.lower() == "manager":
                import manager.manager_dashboard as manager_dashboard
                manager_dashboard.open_manager_dashboard(user_id)

            elif role.lower() == "member":
                import member.member_dashboard as member_dashboard
                # ✅ Pass both user_id and username
                member_dashboard.open_member_dashboard(member_id=user_id, username=username)

            elif role.lower() == "trainer":
                import trainer.trainer_dashboard as trainer_dashboard
                trainer_dashboard.open_trainer_dashboard(user_id)

            elif role.lower() == "attendant":
                import attendant.attendant_dashboard as attendant_dashboard
                attendant_dashboard.open_attendant_dashboard(user_id)

            else:
                messagebox.showerror("Error", "Unknown role!")

        else:
            messagebox.showerror("Error", "Invalid username or password")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ----------------- GUI ----------------- #
root = tk.Tk()
root.title("Smart Gym Login")
root.geometry("400x350")
root.configure(bg="#252540")
root.resizable(False, False)

# ----------------- Top Header ----------------- #
header_frame = tk.Frame(root, bg="#7c5dfa", height=60)
header_frame.pack(fill="x")

header_label = tk.Label(
    header_frame, text="Gym Management System", 
    bg="#7c5dfa", fg="white", font=("Segoe UI", 16, "bold")
)
header_label.pack(pady=15)

# ----------------- Welcome Text ----------------- #
welcome_label = tk.Label(
    root, text="Welcome Back!", 
    bg="#252540", fg="white", font=("Segoe UI", 14)
)
welcome_label.pack(pady=(20,10))

# ----------------- Username & Password Fields ----------------- #
tk.Label(root, text="Username", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(10,5))
entry_username = tk.Entry(root, font=("Segoe UI", 12), width=30)
entry_username.pack()

tk.Label(root, text="Password", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(10,5))
entry_password = tk.Entry(root, show="*", font=("Segoe UI", 12), width=30)
entry_password.pack()

# ----------------- Login Button ----------------- #
login_btn = tk.Button(
    root, text="Login", command=login, 
    bg="#7c5dfa", fg="white", font=("Segoe UI", 12, "bold"), width=15
)
login_btn.pack(pady=30)

root.mainloop()
