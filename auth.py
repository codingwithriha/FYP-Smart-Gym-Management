import tkinter as tk
from tkinter import messagebox
from database_db import get_connection

# ----------------- Login Function ----------------- #
def login():
    username = entry_username.get()
    password = entry_password.get()

    if username.strip() == "" or password.strip() == "":
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT role FROM users
        WHERE username=%s AND password=%s
        """
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            role = user['role']
            messagebox.showinfo("Success", f"Login successful as {role}")

            root.destroy()  # Close login window

            # ----------------- Redirect based on role ----------------- #
            if role == "Admin":
                import admin.admin_dashboard as admin_dashboard
                admin_dashboard.open_admin_dashboard()

            elif role == "Manager":
                import manager.manager_dashboard as manager_dashboard
                manager_dashboard.open_manager_dashboard()

            elif role == "Member":
                import member.member_dashboard as member_dashboard
                member_dashboard.open_member_dashboard()

            elif role == "Trainer":
                import trainer.trainer_dashboard as trainer_dashboard
                trainer_dashboard.open_trainer_dashboard()

            elif role == "Attendant":
                import attendant.attendant_dashboard as attendant_dashboard
                attendant_dashboard.open_attendant_dashboard()

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

header_label = tk.Label(header_frame, text="Gym Management System", 
                        bg="#7c5dfa", fg="white", font=("Arial", 16, "bold"))
header_label.pack(pady=15)

# ----------------- Welcome Text ----------------- #
welcome_label = tk.Label(root, text="Welcome Back!", bg="#252540", 
                         fg="white", font=("Arial", 14))
welcome_label.pack(pady=(20,10))

# ----------------- Username & Password Fields ----------------- #
tk.Label(root, text="Username", bg="#252540", fg="white", font=("Arial", 12)).pack(pady=(10,5))
entry_username = tk.Entry(root, font=("Arial", 12), width=30)
entry_username.pack()

tk.Label(root, text="Password", bg="#252540", fg="white", font=("Arial", 12)).pack(pady=(10,5))
entry_password = tk.Entry(root, show="*", font=("Arial", 12), width=30)
entry_password.pack()

# ----------------- Login Button ----------------- #
login_btn = tk.Button(root, text="Login", command=login, 
                      bg="#7c5dfa", fg="white", font=("Arial", 12, "bold"), width=15)
login_btn.pack(pady=30)

root.mainloop()
