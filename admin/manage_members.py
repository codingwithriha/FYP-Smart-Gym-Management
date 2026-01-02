import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_members(content):

    # ============ CLEAR PAGE ============
    for widget in content.winfo_children():
        widget.destroy()
    content.configure(bg="#1e1e2f")

    # ============ TITLE ============
    tk.Label(
        content,
        text="Managing Members",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ============ FILTER BAR ============
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(filter_frame, text="Filter by Status:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

    status_filter = ttk.Combobox(
        filter_frame,
        values=["All", "Active", "Inactive"],
        state="readonly",
        width=15
    )
    status_filter.set("All")
    status_filter.pack(side="left", padx=5)

    tk.Label(filter_frame, text="Search by Member ID:", bg="#1e1e2f", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=10)

    tk.Button(
        filter_frame,
        text="Search",
        bg="#7E57C2",
        fg="white",
        bd=0,
        padx=20,
        command=lambda: load_members_table()
    ).pack(side="left")

    # ============ FORM ============
    form_frame = tk.Frame(content, bg="#252540")
    form_frame.pack(fill="x", padx=30, pady=20)

    def label(text, r, c):
        tk.Label(form_frame, text=text, bg="#252540", fg="white")\
            .grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def entry(r, c):
        e = tk.Entry(form_frame, width=25)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    label("Member ID", 0, 0)
    member_id = entry(0, 1)

    label("Membership Type", 0, 2)
    membership_type = ttk.Combobox(
        form_frame,
        values=["Basic", "Premium", "Pro"],
        state="readonly",
        width=23
    )
    membership_type.grid(row=0, column=3, padx=10, pady=8)
    membership_type.set("Basic")

    label("Start Date", 1, 0)
    start_date = entry(1, 1)

    label("End Date", 1, 2)
    end_date = entry(1, 3)

    label("Status", 2, 0)
    status = ttk.Combobox(
        form_frame,
        values=["Active", "Inactive"],
        state="readonly",
        width=23
    )
    status.grid(row=2, column=1, padx=10, pady=8)
    status.set("Active")

    label("Emergency Contact", 2, 2)
    emergency_contact = entry(2, 3)

    label("Gym ID", 3, 0)
    gym_id = entry(3, 1)

    label("Zone ID", 3, 2)
    zone_id = entry(3, 3)

    label("Trainer ID", 4, 0)
    trainer_id = entry(4, 1)

    # ============ BUTTONS ============
    btn_frame = tk.Frame(content, bg="#1e1e2f")
    btn_frame.pack(anchor="w", padx=30, pady=15)

    def btn(text, color, cmd):
        tk.Button(btn_frame, text=text, bg=color, fg="white",
                  padx=18, pady=8, bd=0, command=cmd)\
            .pack(side="left", padx=5)

    # ============ TABLE ============
    table_frame = tk.Frame(content, bg="#2f2f4f")
    table_frame.pack(fill="both", expand=True, padx=30, pady=20)

    columns = (
        "member_id", "membership_type", "start_date",
        "end_date", "status", "emergency_contact",
        "gym_id", "zone_id", "trainer_id"
    )

    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=130)

    tree.pack(fill="both", expand=True)

    # ============ FUNCTIONS ============
    def clear_form():
        for e in [member_id, start_date, end_date,
                  emergency_contact, gym_id, zone_id, trainer_id]:
            e.delete(0, tk.END)
        membership_type.set("Basic")
        status.set("Active")

    def load_members_table():
        tree.delete(*tree.get_children())

        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT member_id, membership_type,
                   membership_start_date, membership_end_date,
                   status, emergency_contact,
                   gym_id, zone_id, trainer_id
                   FROM members"""
        conditions = []
        params = []

        # 🔹 FILTER
        if status_filter.get() != "All":
            conditions.append("status=%s")
            params.append(status_filter.get())

        # 🔹 SEARCH
        search_text = search_entry.get().strip()
        if search_text:
            conditions.append("member_id LIKE %s")
            params.append(f"%{search_text}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY member_id DESC"

        cur.execute(query, params)
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)

        conn.close()

    def add_member():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO members
               (membership_type, membership_start_date,
                membership_end_date, status,
                emergency_contact, gym_id, zone_id, trainer_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (membership_type.get(), start_date.get(), end_date.get(),
             status.get(), emergency_contact.get(),
             gym_id.get(), zone_id.get(), trainer_id.get())
        )
        conn.commit()
        conn.close()
        load_members_table()
        clear_form()
        messagebox.showinfo("Success", "Member added successfully")

    def update_member():
        if not member_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE members SET
               membership_type=%s,
               membership_start_date=%s,
               membership_end_date=%s,
               status=%s,
               emergency_contact=%s,
               gym_id=%s,
               zone_id=%s,
               trainer_id=%s
               WHERE member_id=%s""",
            (membership_type.get(), start_date.get(), end_date.get(),
             status.get(), emergency_contact.get(),
             gym_id.get(), zone_id.get(), trainer_id.get(),
             member_id.get())
        )
        conn.commit()
        conn.close()
        load_members_table()
        messagebox.showinfo("Updated", "Member updated successfully")

    def delete_member():
        if not member_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this member?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM members WHERE member_id=%s", (member_id.get(),))
        conn.commit()
        conn.close()
        load_members_table()
        clear_form()

    def on_select(e):
        data = tree.item(tree.focus())["values"]
        if not data:
            return
        clear_form()
        member_id.insert(0, data[0])
        membership_type.set(data[1])
        start_date.insert(0, data[2])
        end_date.insert(0, data[3])
        status.set(data[4])
        emergency_contact.insert(0, data[5])
        gym_id.insert(0, data[6])
        zone_id.insert(0, data[7])
        trainer_id.insert(0, data[8])

    tree.bind("<<TreeviewSelect>>", on_select)

    # ============ BUTTONS ============
    btn("Add", "#7E57C2", add_member)
    btn("Update", "#FFA726", update_member)
    btn("Delete", "#EF5350", delete_member)
    btn("Refresh", "#607D8B", load_members_table)

    # 🔹 LIVE FILTER & SEARCH
    status_filter.bind("<<ComboboxSelected>>", lambda e: load_members_table())
    search_entry.bind("<KeyRelease>", lambda e: load_members_table())

    # 🔹 Load initial data
    load_members_table()
