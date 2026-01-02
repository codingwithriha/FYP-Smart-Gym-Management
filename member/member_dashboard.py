import tkinter as tk

def open_member_dashboard():
    win = tk.Tk()
    win.title("Member Dashboard")
    tk.Label(win, text="Welcome Member").pack(pady=20)
    win.mainloop()
