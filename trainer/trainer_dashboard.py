import tkinter as tk

def open_trainer_dashboard():
    win = tk.Tk()
    win.title("Trainer Dashboard")
    tk.Label(win, text="Welcome Trainer").pack(pady=20)
    win.mainloop()
