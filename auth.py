import tkinter as tk
from tkinter import messagebox
from database_db import get_connection

def login():
    username = entry_username.get()
    password = entry_password.get()

    if username == "" or password == "":
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

            root.destroy()

            if role == "Admin":
                import admin.admin_dashboard as admin_dashboard
                admin_dashboard.open_admin_dashboard()

            elif role == "BRANCH_ADMIN":
                import branch_dashboard
                branch_dashboard.open_branch_dashboard()

            elif role == "MEMBER":
                import member_dashboard
                member_dashboard.open_member_dashboard()

        else:
            messagebox.showerror("Error", "Invalid username or password")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Smart Gym Login")
root.geometry("300x200")

tk.Label(root, text="Username").pack(pady=5)
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password").pack(pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()
