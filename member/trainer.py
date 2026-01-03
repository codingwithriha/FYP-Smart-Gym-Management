import tkinter as tk
from tkinter import messagebox
from database_db import get_connection
from datetime import datetime

def load_trainer_page(content, member_id):
    # ---------------- CLEAR CONTENT ----------------
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1f1b2e")

    # ---------------- PAGE TITLE ----------------
    tk.Label(
        content,
        text="Trainer Information",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(anchor="w", padx=30, pady=(20,10))

    # ---------------- FETCH TRAINER INFO ----------------
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.trainer_id, t.name, t.qualification, t.specialization, t.experience_years
            FROM trainers t
            JOIN users u ON u.trainer_id = t.trainer_id
            WHERE u.id = %s
        """, (member_id,))
        trainer = cursor.fetchone()
        conn.close()

        if not trainer:
            tk.Label(
                content,
                text="No trainer assigned yet.",
                bg="#1f1b2e",
                fg="white",
                font=("Segoe UI", 14)
            ).pack(pady=20)
            return
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch trainer info: {str(e)}")
        return

    # ---------------- TRAINER INFO CARD ----------------
    info_card = tk.Frame(content, bg="#2a2440", height=120, bd=0)
    info_card.pack(fill="x", padx=30, pady=(0,20))
    info_card.pack_propagate(False)

    tk.Label(info_card, text=f"Name: {trainer['name']}", bg="#2a2440", fg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10,0))
    tk.Label(info_card, text=f"Qualification: {trainer['qualification']}", bg="#2a2440", fg="#c7c5dd", font=("Segoe UI", 11)).pack(anchor="w", padx=15, pady=(2,0))
    tk.Label(info_card, text=f"Specialization: {trainer['specialization']}", bg="#2a2440", fg="#c7c5dd", font=("Segoe UI", 11)).pack(anchor="w", padx=15, pady=(2,0))
    tk.Label(info_card, text=f"Experience: {trainer['experience_years']} Years", bg="#2a2440", fg="#c7c5dd", font=("Segoe UI", 11)).pack(anchor="w", padx=15, pady=(2,10))

    # ---------------- CHAT HEADING ----------------
    tk.Label(
        content,
        text=f"Chat with {trainer['name']}",
        bg="#1f1b2e",
        fg="white",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", padx=30, pady=(0,10))

    # ---------------- CHAT AREA ----------------
    chat_frame = tk.Frame(content, bg="#1f1b2e")
    chat_frame.pack(fill="both", expand=True, padx=30, pady=(0,10))

    canvas = tk.Canvas(chat_frame, bg="#1f1b2e", highlightthickness=0)
    scroll = tk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
    scroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=scroll.set)

    messages_frame = tk.Frame(canvas, bg="#1f1b2e")
    canvas.create_window((0,0), window=messages_frame, anchor="nw")

    def resize_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    messages_frame.bind("<Configure>", resize_canvas)

    # ---------------- MESSAGE ENTRY ----------------
    input_frame = tk.Frame(content, bg="#1f1b2e")
    input_frame.pack(fill="x", padx=30, pady=(0,20))

    msg_var = tk.StringVar()
    entry_msg = tk.Entry(input_frame, textvariable=msg_var, font=("Segoe UI", 12), bg="#2a2440", fg="white")
    entry_msg.pack(side="left", fill="x", expand=True, padx=(0,10), pady=5)

    # ---------------- MESSAGE BUBBLES ----------------
    def add_bubble(parent, text, sender="member", timestamp=None, status=None):
        bubble_frame = tk.Frame(parent, bg="#1f1b2e")
        bubble_frame.pack(fill="x", pady=3, anchor="w" if sender=="trainer" else "e")

        # Rounded bubble using Label + padding
        bg_color = "#3a3aff" if sender=="member" else "#3a3a55"
        fg_color = "white"
        justify = "right" if sender=="member" else "left"

        bubble = tk.Label(
            bubble_frame,
            text=text,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 11),
            wraplength=400,
            justify=justify,
            padx=10,
            pady=6,
            bd=0,
            relief="ridge"
        )
        bubble.pack(anchor="e" if sender=="member" else "w", padx=5)

        # Timestamp + status
        ts_text = ""
        if timestamp:
            ts_text += timestamp
        if status:
            ts_text += f" {status}"
        if ts_text:
            tk.Label(bubble_frame, text=ts_text, bg="#1f1b2e", fg="#c7c5dd", font=("Segoe UI", 8)).pack(anchor="e" if sender=="member" else "w", padx=5)

    # ---------------- LOAD CHAT ----------------
    def load_chat():
        for widget in messages_frame.winfo_children():
            widget.destroy()
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT sender, message, created_at, status
                FROM trainer_messages
                WHERE member_id=%s AND trainer_id=%s
                ORDER BY created_at ASC
            """, (member_id, trainer['trainer_id']))
            chats = cursor.fetchall()
            conn.close()

            for msg in chats:
                sender = "member" if msg['sender']=="member" else "trainer"
                ts = msg['created_at'].strftime("%Y-%m-%d %H:%M")
                status = f"[{msg['status'].capitalize()}]" if sender=="member" else ""
                add_bubble(messages_frame, msg['message'], sender=sender, timestamp=ts, status=status)

            canvas.update_idletasks()
            canvas.yview_moveto(1.0)  # scroll to bottom
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load chat: {str(e)}")

    # ---------------- SEND MESSAGE ----------------
    def send_message():
        text = msg_var.get().strip()
        if not text:
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trainer_messages (member_id, trainer_id, message, sender, status)
                VALUES (%s, %s, %s, 'member', 'sent')
            """, (member_id, trainer['trainer_id'], text))
            conn.commit()
            conn.close()
            msg_var.set("")
            load_chat()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

    # ---------------- BUTTONS ----------------
    tk.Button(input_frame, text="Send", bg="#7c5dfa", fg="white", font=("Segoe UI", 12, "bold"),
              padx=15, pady=5, bd=0, activebackground="#5b47c6", activeforeground="white", command=send_message).pack(side="left", padx=(0,10))
    tk.Button(input_frame, text="Refresh", bg="#7c5dfa", fg="white", font=("Segoe UI", 12, "bold"),
              padx=15, pady=5, bd=0, activebackground="#5b47c6", activeforeground="white", command=load_chat).pack(side="left")

    # ---------------- INITIAL LOAD ----------------
    load_chat()
