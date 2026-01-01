import tkinter as tk

def open_branch_dashboard():
    win = tk.Tk()
    win.title("Branch Admin Dashboard")
    tk.Label(win, text="Welcome Branch Admin").pack(pady=20)
    win.mainloop()
