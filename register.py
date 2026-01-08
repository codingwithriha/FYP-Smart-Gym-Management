import tkinter as tk
from tkinter import messagebox
from database_db import get_connection
import auth

# ----------------- REGISTER FUNCTION -----------------
def register_user(reg_win, username_entry, email_entry, password_entry, role_var):
    username = username_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    role = role_var.get()

    if not username or not email or not password:
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Insert into users table for all roles
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s,%s,%s,%s)",
            (username, email, password, role)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"{role.capitalize()} registered successfully!")
        reg_win.destroy()
        auth.open_login_page()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ----------------- OPEN REGISTER PAGE -----------------
def open_register_page():
    reg_win = tk.Tk()
    reg_win.title("Smart Gym - Register")
    reg_win.geometry("400x450")
    reg_win.configure(bg="#252540")
    reg_win.resizable(False, False)

    tk.Label(reg_win, text="Register New User", bg="#7c5dfa", fg="white",
             font=("Segoe UI", 16, "bold")).pack(fill="x", pady=10)

    tk.Label(reg_win, text="Username", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(15,5))
    entry_username = tk.Entry(reg_win, font=("Segoe UI", 12), width=30)
    entry_username.pack()

    tk.Label(reg_win, text="Email", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(10,5))
    entry_email = tk.Entry(reg_win, font=("Segoe UI", 12), width=30)
    entry_email.pack()

    tk.Label(reg_win, text="Password", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(10,5))
    entry_password = tk.Entry(reg_win, show="*", font=("Segoe UI", 12), width=30)
    entry_password.pack()

    tk.Label(reg_win, text="Role", bg="#252540", fg="white", font=("Segoe UI", 12)).pack(pady=(10,5))
    role_var = tk.StringVar()
    role_var.set("member")
    roles = ["admin", "manager", "member", "trainer", "attendant"]
    tk.OptionMenu(reg_win, role_var, *roles).pack(pady=(0,10))

    tk.Button(reg_win, text="Register", bg="#7c5dfa", fg="white",
              font=("Segoe UI", 12, "bold"), width=15,
              command=lambda: register_user(reg_win, entry_username, entry_email, entry_password, role_var)).pack(pady=20)

    tk.Label(reg_win, text="Already have an account?", bg="#252540", fg="white", font=("Segoe UI", 10)).pack()
    tk.Button(reg_win, text="Login Here", bg="#252540", fg="#7c5dfa", bd=0,
              font=("Segoe UI", 10, "bold"),
              command=lambda: [reg_win.destroy(), auth.open_login_page()]).pack()

    reg_win.mainloop()


# ----------------- ENTRY POINT -----------------
if __name__ == "__main__":
    open_register_page()
