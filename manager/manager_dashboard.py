import tkinter as tk

def open_manager_dashboard():
    win = tk.Tk()
    win.title("Manager Dashboard")
    tk.Label(win, text="Welcome Manager").pack(pady=20)
    win.mainloop()
