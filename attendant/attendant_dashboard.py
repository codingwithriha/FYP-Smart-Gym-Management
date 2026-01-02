import tkinter as tk

def open_attendant_dashboard():
    win = tk.Tk()
    win.title("Attendant Dashboard")
    tk.Label(win, text="Welcome Attendant").pack(pady=20)
    win.mainloop()
