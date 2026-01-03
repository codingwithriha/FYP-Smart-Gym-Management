import tkinter as tk
from tkinter import messagebox
from database_db import get_connection

def load_profile_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Edit Profile",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 30))

    # ---------------- FETCH CURRENT INFO ----------------
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, email, contact FROM users WHERE id = %s",
            (member_id,)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            current_name = user[0]
            current_email = user[1]
            current_contact = user[2] if user[2] else ""
        else:
            current_name = ""
            current_email = ""
            current_contact = ""

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch profile: {str(e)}")
        return

    # ---------------- FORM FRAME ----------------
    form_frame = tk.Frame(content, bg="#1f1b2e")
    form_frame.pack(padx=30, pady=10, fill="x")

    label_font = ("Segoe UI", 12, "bold")
    entry_font = ("Segoe UI", 12)
    entry_bg = "#2a2440"
    entry_fg = "white"
    entry_bd = 0
    entry_padx = 10
    entry_pady = 6

    # -------- NAME --------
    tk.Label(form_frame, text="Name", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=0, column=0, sticky="w", pady=(0,10))
    entry_name = tk.Entry(form_frame, font=entry_font, bg=entry_bg, fg=entry_fg, bd=entry_bd, insertbackground="white")
    entry_name.grid(row=0, column=1, sticky="ew", pady=(0,10), ipady=entry_pady, padx=(0,20))
    entry_name.insert(0, current_name)

    # -------- CONTACT --------
    tk.Label(form_frame, text="Contact", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=1, column=0, sticky="w", pady=(0,10))
    entry_contact = tk.Entry(form_frame, font=entry_font, bg=entry_bg, fg=entry_fg, bd=entry_bd, insertbackground="white")
    entry_contact.grid(row=1, column=1, sticky="ew", pady=(0,10), ipady=entry_pady, padx=(0,20))
    entry_contact.insert(0, current_contact)

    # -------- EMAIL --------
    tk.Label(form_frame, text="Email", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=2, column=0, sticky="w", pady=(0,10))
    entry_email = tk.Entry(form_frame, font=entry_font, bg=entry_bg, fg=entry_fg, bd=entry_bd, insertbackground="white")
    entry_email.grid(row=2, column=1, sticky="ew", pady=(0,10), ipady=entry_pady, padx=(0,20))
    entry_email.insert(0, current_email)

    # Make columns expand
    form_frame.columnconfigure(1, weight=1)

    # ---------------- SAVE BUTTON ----------------
    def save_profile():
        new_name = entry_name.get().strip()
        new_contact = entry_contact.get().strip()
        new_email = entry_email.get().strip()

        if not new_name or not new_email:
            messagebox.showerror("Error", "Name and Email are required")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET username=%s, email=%s, contact=%s WHERE id=%s",
                (new_name, new_email, new_contact, member_id)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Profile updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update profile: {str(e)}")

    save_btn = tk.Button(
        content,
        text="Save Profile",
        bg="#7c5dfa",
        fg="white",
        font=("Segoe UI", 13, "bold"),
        command=save_profile,
        activebackground="#5b47c6",
        activeforeground="white",
        bd=0,
        padx=25,
        pady=10
    )
    save_btn.pack(pady=25)
