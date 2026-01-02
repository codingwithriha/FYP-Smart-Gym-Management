import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys, os
import json
import csv
from fpdf import FPDF

# Allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_db import get_connection


def load_manage_reports(content):

    # ================= CLEAR PAGE =================
    for widget in content.winfo_children():
        widget.destroy()

    content.configure(bg="#1e1e2f")

    # ================= TITLE =================
    tk.Label(
        content,
        text="Manage Reports",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 10))

    # ================= FILTER BAR =================
    filter_frame = tk.Frame(content, bg="#1e1e2f")
    filter_frame.pack(fill="x", padx=30, pady=10)

    tk.Label(
        filter_frame,
        text="Filter by Report Type:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    report_filter = ttk.Combobox(
        filter_frame,
        values=[
            "All",
            "Attendance Summary",
            "Revenue Report",
            "Trainer Performance",
            "Membership Report",
            "Equipment Usage"
        ],
        state="readonly",
        width=25
    )
    report_filter.set("All")
    report_filter.pack(side="left", padx=(0, 15))

    tk.Label(
        filter_frame,
        text="Search by Report ID:",
        bg="#1e1e2f",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(side="left", padx=(0, 5))

    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side="left", padx=(0, 10))

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

    def form_entry(r, c, w=28):
        e = tk.Entry(form_frame, width=w)
        e.grid(row=r, column=c, padx=10, pady=8)
        return e

    # ================= FORM FIELDS =================
    form_label("Report ID", 0, 0)
    report_id = form_entry(0, 1)

    form_label("Report Type", 0, 2)
    report_type = ttk.Combobox(
        form_frame,
        values=[
            "Attendance Summary",
            "Revenue Report",
            "Trainer Performance",
            "Membership Report",
            "Equipment Usage"
        ],
        state="readonly",
        width=25
    )
    report_type.grid(row=0, column=3, padx=10, pady=8)
    report_type.set("Attendance Summary")

    form_label("Gym ID", 1, 0)
    gym_id = form_entry(1, 1)

    form_label("Generated On (YYYY-MM-DD)", 1, 2)
    generated_on = form_entry(1, 3)

    form_label("File Path", 2, 0)
    file_path = form_entry(2, 1)

    form_label("JSON Data", 2, 2)
    json_data = form_entry(2, 3, 45)

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
            "report_id", "report_type", "gym_id",
            "generated_on", "file_path", "json_data"
        ),
        show="headings"
    )

    headings = [
        ("report_id", "Report ID"),
        ("report_type", "Report Type"),
        ("gym_id", "Gym ID"),
        ("generated_on", "Generated On"),
        ("file_path", "File Path"),
        ("json_data", "JSON Data"),
    ]

    for col, text in headings:
        tree.heading(col, text=text)
        tree.column(col, width=170)

    tree.pack(fill="both", expand=True)

    # ================= FUNCTIONS =================
    def clear_form():
        for e in [report_id, gym_id, generated_on, file_path, json_data]:
            e.delete(0, tk.END)
        report_type.set("Attendance Summary")

    def load_reports_table():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()

        query = """SELECT report_id, report_type, gym_id,
                   generated_on, file_path, json_data
                   FROM reports"""
        params = []
        where = []

        if report_filter.get() != "All":
            where.append("report_type=%s")
            params.append(report_filter.get())

        if search_entry.get():
            where.append("report_id LIKE %s")
            params.append(f"%{search_entry.get()}%")

        if where:
            query += " WHERE " + " AND ".join(where)

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    def add_report():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO reports
               (report_type, gym_id, generated_on, file_path, json_data)
               VALUES (%s,%s,%s,%s,%s)""",
            (
                report_type.get(),
                gym_id.get(),
                generated_on.get(),
                file_path.get(),
                json_data.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Report added successfully")
        clear_form()
        load_reports_table()

    def update_report():
        if not report_id.get():
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE reports SET
               report_type=%s, gym_id=%s,
               generated_on=%s, file_path=%s,
               json_data=%s
               WHERE report_id=%s""",
            (
                report_type.get(),
                gym_id.get(),
                generated_on.get(),
                file_path.get(),
                json_data.get(),
                report_id.get()
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Report updated successfully")
        load_reports_table()

    def delete_report():
        if not report_id.get():
            return
        if not messagebox.askyesno("Confirm", "Delete this report?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM reports WHERE report_id=%s", (report_id.get(),))
        conn.commit()
        conn.close()
        clear_form()
        load_reports_table()

    def on_row_select(event):
        selected = tree.focus()
        if not selected:
            return
        data = tree.item(selected)["values"]
        clear_form()
        report_id.insert(0, data[0])
        report_type.set(data[1])
        gym_id.insert(0, data[2])
        generated_on.insert(0, data[3])
        file_path.insert(0, data[4])
        json_data.insert(0, data[5])

    def view_report():
        if not json_data.get():
            messagebox.showerror("Error", "No JSON data found")
            return
        win = tk.Toplevel()
        win.title("View Report JSON")
        win.geometry("600x450")
        text = tk.Text(win, wrap="word")
        text.pack(fill="both", expand=True)
        text.insert("1.0", json.dumps(json.loads(json_data.get()), indent=4))

    def export_csv():
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM reports")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cur.description])
            writer.writerows(cur.fetchall())
        conn.close()
        messagebox.showinfo("Exported", "CSV exported successfully")

    def export_pdf():
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not path:
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM reports")
        rows = cur.fetchall()
        headers = [i[0] for i in cur.description]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Smart Gym Reports", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", size=8)
        for h in headers:
            pdf.cell(38, 8, h, border=1)
        pdf.ln()

        for row in rows:
            for col in row:
                pdf.cell(38, 8, str(col)[:40], border=1)
            pdf.ln()

        pdf.output(path)
        conn.close()
        messagebox.showinfo("Exported", "PDF exported successfully")

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= LIVE SEARCH & FILTER =================
    search_entry.bind("<KeyRelease>", lambda e: load_reports_table())
    report_filter.bind("<<ComboboxSelected>>", lambda e: load_reports_table())

    # ================= BUTTONS =================
    action_btn("Add Report", "#2196F3", add_report)
    action_btn("Update", "#FF9800", update_report)
    action_btn("Delete", "#F44336", delete_report)
    action_btn("Clear", "#607D8B", clear_form)
    action_btn("View Report", "#673AB7", view_report)
    action_btn("Export CSV", "#009688", export_csv)
    action_btn("Export PDF", "#795548", export_pdf)

    load_reports_table()
