import tkinter as tk
from tkinter import messagebox
from database_db import get_connection

# ================= RESET PASSWORD PAGE =================
def load_reset_password(parent, trainer_id):
    """
    Load Reset Password page for the logged-in trainer
    parent     : Tkinter frame where page is loaded
    trainer_id : ID of the logged-in trainer
    """

    # Clear page
    for widget in parent.winfo_children():
        widget.destroy()

    # ---------------- THEME ----------------
    BG = "#1e1e2f"
    CARD = "#2a2a3f"
    ACCENT = "#7c5dfa"
    TEXT = "#ffffff"
    INPUT_BG = "#33334d"
    BORDER = "#444466"

    parent.configure(bg=BG)

    # ---------------- MAIN CONTAINER ----------------
    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True, padx=25, pady=25)

    tk.Label(
        main,
        text="Reset Password",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", pady=(0, 20))

    form = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    form.pack(fill="both", padx=10, pady=10, ipadx=10, ipady=10)

    # ------------------ Fetch Trainer Info ------------------
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, password FROM trainers WHERE trainer_id=%s", (trainer_id,))
        trainer = cursor.fetchone()
        if not trainer:
            messagebox.showerror("Error", "Trainer not found")
            return
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    # ---------- Username (read-only) ----------
    tk.Label(form, text="Username", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=10, padx=10)
    username_entry = tk.Entry(form, bg=INPUT_BG, fg=BG, relief="flat")
    username_entry.grid(row=0, column=1, pady=10, padx=10)
    username_entry.insert(0, trainer["name"])
    username_entry.config(state="readonly")

    # ---------- Old Password ----------
    tk.Label(form, text="Old Password", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10, padx=10)
    old_pass_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT, relief="flat", show="*")
    old_pass_entry.grid(row=1, column=1, pady=10, padx=10)

    # ---------- New Password ----------
    tk.Label(form, text="New Password", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=10, padx=10)
    new_pass_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT, relief="flat", show="*")
    new_pass_entry.grid(row=2, column=1, pady=10, padx=10)

    # ---------- Confirm Password ----------
    tk.Label(form, text="Confirm Password", bg=CARD, fg=ACCENT,
             font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=10, padx=10)
    confirm_pass_entry = tk.Entry(form, bg=INPUT_BG, fg=TEXT, relief="flat", show="*")
    confirm_pass_entry.grid(row=3, column=1, pady=10, padx=10)

    # ---------- Show/Hide Toggle ----------
    def toggle_password():
        for e in [old_pass_entry, new_pass_entry, confirm_pass_entry]:
            e.config(show="" if e.cget("show") == "*" else "*")

    toggle_btn = tk.Button(form, text="Show/Hide Password", bg=ACCENT, fg=TEXT,
                           relief="flat", command=toggle_password)
    toggle_btn.grid(row=4, column=0, columnspan=2, pady=(0, 10))

    # ---------- RESET BUTTON ----------
    def reset_password():
        old_pass = old_pass_entry.get()
        new_pass = new_pass_entry.get()
        confirm_pass = confirm_pass_entry.get()

        if not old_pass or not new_pass or not confirm_pass:
            messagebox.showerror("Error", "All fields are required")
            return

        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New Password and Confirm Password do not match")
            return

        # Verify old password
        if old_pass != trainer["password"]:
            messagebox.showerror("Error", "Old Password is incorrect")
            return

        try:
            cursor.execute("UPDATE trainers SET password=%s WHERE trainer_id=%s", (new_pass, trainer_id))
            conn.commit()
            messagebox.showinfo("Success", "Password updated successfully")

            # Clear fields
            old_pass_entry.delete(0, tk.END)
            new_pass_entry.delete(0, tk.END)
            confirm_pass_entry.delete(0, tk.END)

            # Update trainer object
            trainer["password"] = new_pass

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(form, text="Reset Password", bg=ACCENT, fg=TEXT,
              font=("Segoe UI", 11, "bold"), relief="flat",
              pady=8, command=reset_password).grid(row=5, column=0, columnspan=2, pady=20)
