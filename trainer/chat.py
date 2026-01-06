import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database_db import get_connection

def load_chat(parent, trainer_id):
    for w in parent.winfo_children():
        w.destroy()

    # ---------------- COLORS ----------------
    BG = "#1e1e2f"
    SIDEBAR = "#23233a"
    CARD = "#2a2a3f"
    ACCENT = "#7c5dfa"
    TEXT = "#ffffff"
    MUTED = "#9fa0b5"
    INPUT_BG = "#33334d"

    parent.configure(bg=BG)

    # ---------------- MAIN ----------------
    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True, padx=20, pady=20)
    main.columnconfigure(0, weight=1)
    main.columnconfigure(1, weight=3)

    # ================= LEFT (MEMBERS) =================
    left = tk.Frame(main, bg=SIDEBAR)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    tk.Label(left, text="My Members", bg=SIDEBAR, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(pady=(15, 10))

    members_list = tk.Listbox(
        left, bg=SIDEBAR, fg=TEXT,
        selectbackground=ACCENT,
        font=("Segoe UI", 11),
        relief="flat", highlightthickness=0
    )
    members_list.pack(fill="both", expand=True, padx=10, pady=10)

    # ================= RIGHT (CHAT) =================
    right = tk.Frame(main, bg=CARD)
    right.grid(row=0, column=1, sticky="nsew")

    # ---- HEADER ----
    header = tk.Frame(right, bg=ACCENT, height=60)
    header.pack(fill="x")

    chat_title = tk.Label(header, text="Select a member",
                          bg=ACCENT, fg=TEXT,
                          font=("Segoe UI", 13, "bold"))
    chat_title.pack(pady=(10, 0))

    typing_lbl = tk.Label(header, text="",
                          bg=ACCENT, fg="#e0dcff",
                          font=("Segoe UI", 9))
    typing_lbl.pack()

    # ---- CHAT BODY ----
    chat_body = tk.Frame(right, bg=CARD)
    chat_body.pack(fill="both", expand=True, padx=15, pady=15)

    canvas = tk.Canvas(chat_body, bg=CARD, highlightthickness=0)
    scrollbar = ttk.Scrollbar(chat_body, command=canvas.yview)
    msg_frame = tk.Frame(canvas, bg=CARD)

    msg_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=msg_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---- INPUT ----
    input_frame = tk.Frame(right, bg=BG)
    input_frame.pack(fill="x", padx=15, pady=15)

    msg_entry = tk.Entry(input_frame, bg=INPUT_BG, fg=MUTED,
                         font=("Segoe UI", 11), relief="flat")
    msg_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
    msg_entry.insert(0, "Type your message here...")

    send_btn = tk.Button(input_frame, text="Send",
                         bg=ACCENT, fg=TEXT,
                         font=("Segoe UI", 11, "bold"),
                         relief="flat", padx=25)
    send_btn.pack(side="right")

    # ---------------- STATE ----------------
    selected = {"id": None, "name": ""}

    # ================= FUNCTIONS =================
    def load_members():
        members_list.delete(0, tk.END)
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT m.member_id, m.name,
            (SELECT message FROM messages
             WHERE (sender_id=m.member_id AND receiver_id=%s)
             OR (sender_id=%s AND receiver_id=m.member_id)
             ORDER BY created_at DESC LIMIT 1) last_msg
            FROM members m WHERE m.trainer_id=%s
        """, (trainer_id, trainer_id, trainer_id))
        for r in cur.fetchall():
            preview = r["last_msg"][:20]+"..." if r["last_msg"] else "No messages"
            members_list.insert(tk.END, f"{r['member_id']} - {r['name']}  |  {preview}")
        conn.close()

    def load_messages():
        for w in msg_frame.winfo_children():
            w.destroy()
        if not selected["id"]:
            return

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT sender_id, message, created_at, status
            FROM messages
            WHERE (sender_id=%s AND receiver_id=%s)
            OR (sender_id=%s AND receiver_id=%s)
            ORDER BY created_at
        """, (trainer_id, selected["id"], selected["id"], trainer_id))
        rows = cur.fetchall()

        # mark seen
        cur.execute("""
            UPDATE messages SET status='Seen'
            WHERE receiver_id=%s AND sender_id=%s
        """, (trainer_id, selected["id"]))
        conn.commit()
        conn.close()

        for r in rows:
            align = "e" if r["sender_id"] == trainer_id else "w"
            bg = ACCENT if r["sender_id"] == trainer_id else "#3a3a55"
            bubble = tk.Frame(msg_frame, bg=CARD)
            bubble.pack(anchor=align, pady=5, padx=10)

            tk.Label(bubble, text=r["message"], bg=bg, fg=TEXT,
                     wraplength=350, padx=10, pady=6,
                     font=("Segoe UI", 10)).pack(anchor=align)

            meta = f"{r['created_at'].strftime('%H:%M')} • {r['status']}"
            tk.Label(bubble, text=meta, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 8)).pack(anchor=align)

        canvas.yview_moveto(1)

    def select_member(e):
        sel = members_list.get(members_list.curselection())
        mid, rest = sel.split(" - ", 1)
        selected["id"] = int(mid)
        selected["name"] = rest.split("|")[0].strip()
        chat_title.config(text=f"Chat with {selected['name']}")
        load_messages()

    def send_message():
        text = msg_entry.get().strip()
        if not text or text == "Type your message here...":
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages
            (sender_id, receiver_id, user_id, message, created_at, status)
            VALUES (%s,%s,%s,%s,%s,'Sent')
        """, (trainer_id, selected["id"], trainer_id, text, datetime.now()))
        conn.commit()
        conn.close()

        msg_entry.delete(0, tk.END)
        typing_lbl.config(text="")
        load_messages()
        load_members()

    # ---------------- EVENTS ----------------
    def on_typing(e):
        typing_lbl.config(text="Typing...")

    def on_focus(e):
        if msg_entry.get() == "Type your message here...":
            msg_entry.delete(0, tk.END)
            msg_entry.config(fg=TEXT)

    def on_blur(e):
        if not msg_entry.get():
            msg_entry.insert(0, "Type your message here...")
            msg_entry.config(fg=MUTED)

    members_list.bind("<<ListboxSelect>>", select_member)
    msg_entry.bind("<Key>", on_typing)
    msg_entry.bind("<FocusIn>", on_focus)
    msg_entry.bind("<FocusOut>", on_blur)
    msg_entry.bind("<Return>", lambda e: send_message())
    send_btn.config(command=send_message)

    load_members()
