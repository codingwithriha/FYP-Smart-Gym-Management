import tkinter as tk
from tkinter import messagebox
from database_db import get_connection
import register

# ----------------- LOGIN FUNCTION -----------------
def login(root, role, username_input, password_input):
    role = role.lower()
    if username_input.strip() == "" or (role != "admin" and password_input.strip() == ""):
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Determine table and ID column based on role
        if role == "member":
            table = "members"
            id_col = "member_id"
        elif role == "trainer":
            table = "trainers"
            id_col = "trainer_id"
        elif role == "attendant":
            table = "attendants"
            id_col = "attendant_id"
        elif role == "manager":
            table = "managers"
            id_col = "manager_id"
        elif role == "admin":
            table = "users"
            id_col = "id"
        else:
            messagebox.showerror("Error", "Invalid role selected!")
            return

        # Build query
        if role == "admin":
            query = f"SELECT id, username, role FROM {table} WHERE username=%s AND password=%s"
            cursor.execute(query, (username_input, password_input))
        else:
            query = f"SELECT * FROM {table} WHERE {id_col}=%s AND password=%s"
            cursor.execute(query, (username_input, password_input))

        user = cursor.fetchone()
        conn.close()

        if user:
            root.destroy()
            user_id = user[id_col] if role != "admin" else user["id"]

            # Redirect to dashboards
            if role == "admin":
                import admin.admin_dashboard as admin_dashboard
                admin_dashboard.open_admin_dashboard()
            elif role == "manager":
                import manager.manager_dashboard as manager_dashboard
                manager_dashboard.open_manager_dashboard(user_id)
            elif role == "member":
                import member.member_dashboard as member_dashboard
                member_dashboard.open_member_dashboard(member_id=user_id)
            elif role == "trainer":
                import trainer.trainer_dashboard as trainer_dashboard
                trainer_dashboard.open_trainer_dashboard(user_id)
            elif role == "attendant":
                import attendant.attendant_dashboard as attendant_dashboard
                attendant_dashboard.open_attendant_dashboard(user_id)
        else:
            messagebox.showerror("Error", "Invalid credentials for the selected role!")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ----------------- OPEN LOGIN PAGE -----------------
def open_login_page():
    root = tk.Tk()
    root.title("Smart Gym Login")
    root.geometry("400x450")
    root.configure(bg="#252540")
    root.resizable(False, False)

    # Header
    tk.Label(root, text="Smart Gym Management", bg="#7c5dfa", fg="white",
             font=("Segoe UI", 16, "bold")).pack(fill="x", pady=15)

    # Role Dropdown
    tk.Label(root, text="Select Role", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(10,5))
    role_var = tk.StringVar()
    role_var.set("member")
    roles = ["admin", "manager", "member", "trainer", "attendant"]
    tk.OptionMenu(root, role_var, *roles).pack(pady=(0,15))

    # Username / ID
    tk.Label(root, text="Username / ID", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(5,5))
    entry_username = tk.Entry(root, font=("Segoe UI", 12), width=30)
    entry_username.pack()

    # Password
    tk.Label(root, text="Password", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(10,5))
    entry_password = tk.Entry(root, show="*", font=("Segoe UI", 12), width=30)
    entry_password.pack()

    # Login Button
    tk.Button(root, text="Login", bg="#7c5dfa", fg="white", font=("Segoe UI", 12, "bold"), width=15,
              command=lambda: login(root, role_var.get(), entry_username.get(), entry_password.get())).pack(pady=20)

    # Register link
    tk.Label(root, text="New User?", bg="#252540", fg="white", font=("Segoe UI", 10)).pack()
    tk.Button(root, text="Register Here", bg="#252540", fg="#7c5dfa", bd=0,
              font=("Segoe UI", 10, "bold"),
              command=lambda: [root.destroy(), register.open_register_page()]).pack()

    root.mainloop()


# ----------------- ENTRY POINT -----------------
if __name__ == "__main__":
    open_login_page()
