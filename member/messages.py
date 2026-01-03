import tkinter as tk
from tkinter import ttk, messagebox
from database_db import get_connection
from datetime import datetime

def load_messages_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Message to Branch Manager",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))  # smaller pady

    # ---------------- FORM FRAME ----------------
    form_frame = tk.Frame(content, bg="#1f1b2e")
    form_frame.pack(padx=30, pady=(0,5), fill="x")  # reduced pady

    label_font = ("Segoe UI", 12, "bold")
    entry_font = ("Segoe UI", 12)
    entry_bg = "#2a2440"
    entry_fg = "white"

    # ---------------- DROPDOWNS IN ONE LINE ----------------
    city_var = tk.StringVar()
    area_var = tk.StringVar()
    branch_var = tk.StringVar()

    tk.Label(form_frame, text="City", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=0, column=0, sticky="w")
    tk.Label(form_frame, text="Area", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=0, column=2, sticky="w", padx=(10,0))
    tk.Label(form_frame, text="Branch", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=0, column=4, sticky="w", padx=(10,0))

    city_dropdown = ttk.Combobox(form_frame, textvariable=city_var, state="readonly", width=15)
    area_dropdown = ttk.Combobox(form_frame, textvariable=area_var, state="readonly", width=15)
    branch_dropdown = ttk.Combobox(form_frame, textvariable=branch_var, state="readonly", width=20)

    city_dropdown.grid(row=0, column=1, sticky="w", padx=(5,10))
    area_dropdown.grid(row=0, column=3, sticky="w", padx=(5,10))
    branch_dropdown.grid(row=0, column=5, sticky="w", padx=(5,10))

    form_frame.columnconfigure(1, weight=1)
    form_frame.columnconfigure(3, weight=1)
    form_frame.columnconfigure(5, weight=1)

    # ---------------- FETCH BRANCH DATA ----------------
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT city FROM branches")
        cities = [row['city'] for row in cursor.fetchall()]
        city_dropdown['values'] = cities
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch cities: {str(e)}")
        return

    # ---------------- DROPDOWN LOGIC ----------------
    def update_areas(event):
        selected_city = city_var.get()
        if not selected_city:
            return
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT DISTINCT area FROM branches WHERE city=%s", (selected_city,))
            areas = [row['area'] for row in cursor.fetchall()]
            area_dropdown['values'] = areas
            area_var.set('')
            branch_var.set('')
            branch_dropdown['values'] = []
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_branches(event):
        selected_city = city_var.get()
        selected_area = area_var.get()
        if not selected_city or not selected_area:
            return
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT branch_name FROM branches WHERE city=%s AND area=%s",
                (selected_city, selected_area)
            )
            branches = [row['branch_name'] for row in cursor.fetchall()]
            branch_dropdown['values'] = branches
            branch_var.set('')
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    city_dropdown.bind("<<ComboboxSelected>>", update_areas)
    area_dropdown.bind("<<ComboboxSelected>>", update_branches)

    # ---------------- MESSAGE TEXTAREA ----------------
    tk.Label(form_frame, text="Your Message", bg="#1f1b2e", fg="#c7c5dd", font=label_font).grid(row=1, column=0, sticky="nw", pady=(10,0))
    txt_message = tk.Text(form_frame, height=4, font=entry_font, bg=entry_bg, fg=entry_fg, bd=0, wrap="word", insertbackground="white")
    txt_message.grid(row=1, column=1, columnspan=5, sticky="ew", pady=(10,0))

    # ---------------- SEND MESSAGE BUTTON ----------------
    def send_message():
        city = city_var.get()
        area = area_var.get()
        branch = branch_var.get()
        message = txt_message.get("1.0", tk.END).strip()

        if not city or not area or not branch or not message:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (user_id, branch, city, area, message) VALUES (%s, %s, %s, %s, %s)",
                (member_id, branch, city, area, message)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Message sent successfully!")
            txt_message.delete("1.0", tk.END)
            load_message_history()  # refresh history
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

    tk.Button(
        content,
        text="Send Message",
        bg="#7c5dfa",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        command=send_message,
        padx=20,
        pady=6,  # smaller padding
        bd=0,
        activebackground="#5b47c6",
        activeforeground="white"
    ).pack(pady=10)

    # ---------------- MESSAGE HISTORY ----------------
    tk.Label(content, text="Your Message History", bg="#1f1b2e", fg="white", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=30, pady=(10,5))

    tree_frame = tk.Frame(content, bg="#1f1b2e")
    tree_frame.pack(fill="both", expand=True, padx=30, pady=(0,10))  # reduced pady

    columns = ("branch", "city", "area", "message", "date", "status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    tree.heading("branch", text="Branch")
    tree.heading("city", text="City")
    tree.heading("area", text="Area")
    tree.heading("message", text="Message")
    tree.heading("date", text="Date")
    tree.heading("status", text="Status")

    tree.column("branch", width=100, anchor="center")
    tree.column("city", width=80, anchor="center")
    tree.column("area", width=80, anchor="center")
    tree.column("message", width=300, anchor="w")
    tree.column("date", width=140, anchor="center")
    tree.column("status", width=100, anchor="center")

    tree.pack(side="left", fill="both", expand=True)

    # ---------------- SCROLLBAR ----------------
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # ---------------- LOAD MESSAGE HISTORY ----------------
    def load_message_history():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT branch, city, area, message, created_at, status FROM messages WHERE user_id=%s ORDER BY created_at DESC",
                (member_id,)
            )
            messages = cursor.fetchall()
            conn.close()
            for msg in messages:
                tree.insert("", "end", values=(msg['branch'], msg['city'], msg['area'], msg['message'], msg['created_at'].strftime("%Y-%m-%d %H:%M"), msg['status']))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch messages: {str(e)}")

    load_message_history()
