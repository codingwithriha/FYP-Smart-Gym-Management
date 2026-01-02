import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_workout_zones(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Workout Zones",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    floor_filter = ttk.Combobox(
        filter_frame,
        values=[
            "All",
            "Ground Floor",
            "First Floor",
            "Second Floor",
            "Third Floor",
            "Rooftop"
        ],
        state="readonly",
        width=20
    )
    floor_filter.set("All")
    floor_filter.pack(side="left", padx=(0, 10))

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=(0, 10))

    tk.Button(
        filter_frame,
        text="Search",
        bg="#4CAF50",
        fg="white",
        bd=0,
        padx=20,
        pady=6,
        command=lambda: load_zones_table()
    ).pack(side="left")

    # Enter key search
    search_entry.bind("<Return>", lambda e: load_zones_table())

    # ================= FORM =================
    form_frame = tk.Frame(content, bg="#252540")
    form_frame.pack(fill="x", padx=30, pady=20)

    def form_label(text, r, c):
        tk.Label(
            form_frame,
            text=text,
            bg="#252540",
            fg="white"
        ).grid(row=r, column=c, sticky="w", padx=10, pady=8)

    def form_entry(r, c):
        e = tk.Entry(form_frame, width=28)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    # ================= FORM FIELDS =================
    form_label("Zone ID", 0, 0)
    zone_id = form_entry(0, 1)

    form_label("Zone Name", 0, 2)
    zone_name = ttk.Combobox(
        form_frame,
        values=[
            "Yoga Zone",
            "Martial Arts Zone",
            "Cardio Zone",
            "Weight Training Zone",
            "CrossFit Zone"
        ],
        state="readonly",
        width=25
    )
    zone_name.grid(row=0, column=3, padx=10, pady=8)

    form_label("Zone Type", 1, 0)
    zone_type = form_entry(1, 1)
    zone_type.configure(state="readonly")

    form_label("Gym ID", 1, 2)
    gym_id = form_entry(1, 3)

    form_label("Floor Number", 2, 0)
    floor_number = ttk.Combobox(
        form_frame,
        values=[
            "Ground Floor",
            "First Floor",
            "Second Floor",
            "Third Floor",
            "Rooftop"
        ],
        state="readonly",
        width=25
    )
    floor_number.grid(row=2, column=1, padx=10, pady=8)

    form_label("Announcements", 2, 2)
    announcements = tk.Text(form_frame, width=30, height=3)
    announcements.grid(row=2, column=3, padx=10, pady=8)

    # ================= AUTO ZONE TYPE =================
    def auto_zone_type(event=None):
        zone_type.configure(state="normal")
        zone_type.delete(0, tk.END)
        zone_type.insert(0, zone_name.get())
        zone_type.configure(state="readonly")

    zone_name.bind("<<ComboboxSelected>>", auto_zone_type)

    # ================= BUTTONS =================
    btn_frame = tk.Frame(content, bg="#1e1e2f")
    btn_frame.pack(anchor="w", padx=30, pady=15)

    def action_btn(text, color, cmd):
        tk.Button(
            btn_frame,
            text=text,
            bg=color,
            fg="white",
            bd=0,
            padx=18,
            pady=8,
            command=cmd
        ).pack(side="left", padx=5)

    # ================= TABLE =================
    table_frame = tk.Frame(content, bg="#2f2f4f")
    table_frame.pack(fill="both", expand=True, padx=30, pady=20)

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "zone_id", "zone_name", "zone_type",
            "gym_id", "announcements", "floor"
        ),
        show="headings"
    )

    headings = [
        ("zone_id", "Zone ID"),
        ("zone_name", "Zone Name"),
        ("zone_type", "Zone Type"),
        ("gym_id", "Gym ID"),
        ("announcements", "Announcements"),
        ("floor", "Floor")
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=160)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        zone_id.delete(0, tk.END)
        zone_name.set("")
        zone_type.configure(state="normal")
        zone_type.delete(0, tk.END)
        zone_type.configure(state="readonly")
        gym_id.delete(0, tk.END)
        announcements.delete("1.0", tk.END)
        floor_number.set("")

    def load_zones_table():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT zone_id, zone_name, zone_type,
                   gym_id, announcements, floor_number
            FROM workout_zones
        """

        conditions = []
        params = []

        if floor_filter.get() != "All":
            conditions.append("floor_number = %s")
            params.append(floor_filter.get())

        if search_entry.get().strip():
            conditions.append("zone_name LIKE %s")
            params.append(f"%{search_entry.get().strip()}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY zone_id DESC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_zone():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO workout_zones
               (zone_name, zone_type, gym_id, announcements, floor_number)
               VALUES (%s,%s,%s,%s,%s)""",
            (
                zone_name.get(),
                zone_type.get(),
                gym_id.get(),
                announcements.get("1.0", tk.END).strip(),
                floor_number.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Workout zone added successfully")
        clear_form()
        load_zones_table()

    def update_zone():
        if not zone_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE workout_zones SET
               zone_name=%s,
               zone_type=%s,
               gym_id=%s,
               announcements=%s,
               floor_number=%s
               WHERE zone_id=%s""",
            (
                zone_name.get(),
                zone_type.get(),
                gym_id.get(),
                announcements.get("1.0", tk.END).strip(),
                floor_number.get(),
                zone_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Workout zone updated successfully")
        load_zones_table()

    def delete_zone():
        if not zone_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this workout zone?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM workout_zones WHERE zone_id=%s", (zone_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_zones_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        zone_id.insert(0, data[0])
        zone_name.set(data[1])
        auto_zone_type()
        gym_id.insert(0, data[3])
        announcements.insert("1.0", data[4])
        floor_number.set(data[5])

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= BUTTON WIRING =================
    action_btn("Add Zone", "#2196F3", add_zone)
    action_btn("Update", "#FF9800", update_zone)
    action_btn("Delete", "#F44336", delete_zone)
    action_btn("Clear", "#607D8B", clear_form)

    load_zones_table()
