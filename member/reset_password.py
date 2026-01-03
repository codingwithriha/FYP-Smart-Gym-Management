import tkinter as tk
from tkinter import messagebox
from database_db import get_connection

def load_reset_password_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Reset Password",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 30))

    # ---------------- FORM FRAME ----------------
    form_frame = tk.Frame(content, bg="#1f1b2e")
    form_frame.pack(padx=30, pady=10, fill="x")

    label_font = ("Segoe UI", 12, "bold")
    entry_font = ("Segoe UI", 12)
    entry_bg = "#2a2440"
    entry_fg = "white"
    entry_bd = 0
    entry_ipady = 6

    # -------- OLD PASSWORD --------
    tk.Label(form_frame, text="Old Password", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=0, column=0, sticky="w", pady=(0,10))
    entry_old = tk.Entry(form_frame, font=entry_font, bg=entry_bg, fg=entry_fg, bd=entry_bd, show="*", insertbackground="white")
    entry_old.grid(row=0, column=1, sticky="ew", pady=(0,10), ipady=entry_ipady, padx=(0,5))

    # Eye button for old password
    def toggle_old():
        if entry_old.cget("show") == "*":
            entry_old.config(show="")
        else:
            entry_old.config(show="*")
    btn_eye_old = tk.Button(form_frame, text="👁️", command=toggle_old, bd=0, bg=entry_bg, fg="white", font=("Segoe UI", 10))
    btn_eye_old.grid(row=0, column=2, sticky="w")

    # -------- NEW PASSWORD --------
    tk.Label(form_frame, text="New Password", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=1, column=0, sticky="w", pady=(0,10))
    entry_new = tk.Entry(form_frame, font=entry_font, bg=entry_bg, fg=entry_fg, bd=entry_bd, show="*", insertbackground="white")
    entry_new.grid(row=1, column=1, sticky="ew", pady=(0,10), ipady=entry_ipady, padx=(0,5))

    # Eye button for new password
    def toggle_new():
        if entry_new.cget("show") == "*":
            entry_new.config(show="")
        else:
            entry_new.config(show="*")
    btn_eye_new = tk.Button(form_frame, text="👁️", command=toggle_new, bd=0, bg=entry_bg, fg="white", font=("Segoe UI", 10))
    btn_eye_new.grid(row=1, column=2, sticky="w")

    # Make columns expand
    form_frame.columnconfigure(1, weight=1)

    # ---------------- RESET PASSWORD BUTTON ----------------
    def reset_password():
        old_pass = entry_old.get().strip()
        new_pass = entry_new.get().strip()

        if not old_pass or not new_pass:
            messagebox.showerror("Error", "Both fields are required")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Check old password
            cursor.execute("SELECT password FROM users WHERE id=%s", (member_id,))
            current = cursor.fetchone()
            if not current:
                messagebox.showerror("Error", "User not found")
                conn.close()
                return
            if current[0] != old_pass:
                messagebox.showerror("Error", "Old password is incorrect")
                conn.close()
                return

            # Update password
            cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_pass, member_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password updated successfully!")
            entry_old.delete(0, tk.END)
            entry_new.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset password: {str(e)}")

    tk.Button(
        content,
        text="Reset Password",
        bg="#7c5dfa",
        fg="white",
        font=("Segoe UI", 13, "bold"),
        command=reset_password,
        activebackground="#5b47c6",
        activeforeground="white",
        bd=0,
        padx=25,
        pady=10
    ).pack(pady=25)
