import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
from database_db import get_connection

# ================= TRAINER REPORTS PAGE =================
def load_reports(parent, trainer_id):
    # Clear page
    for widget in parent.winfo_children():
        widget.destroy()

    # ---------------- THEME ----------------
    BG = "#1e1e2f"
    CARD = "#2a2a3f"
    ACCENT = "#7c5dfa"
    TEXT = "#ffffff"
    INPUT_BG = "#33334d"
    BORDER = "#444466"

    parent.configure(bg=BG)

    # ---------------- MAIN CONTAINER ----------------
    main = tk.Frame(parent, bg=BG)
    main.pack(fill="both", expand=True, padx=25, pady=25)

    # ---------- TITLE ----------
    tk.Label(
        main,
        text="Performance Reports",
        bg=BG, fg=TEXT,
        font=("Segoe UI", 18, "bold")
    ).pack(anchor="w", pady=(0,15))

    # ---------------- FILTERS FRAME ----------------
    filter_frame = tk.Frame(main, bg=CARD, pady=10, padx=10)
    filter_frame.pack(fill="x", pady=(0,15))

    # ---------- MEMBER DROPDOWN ----------
    tk.Label(filter_frame, text="Member:", bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
    member_cb = ttk.Combobox(filter_frame, state="readonly", width=22)
    member_cb.grid(row=0, column=1, padx=5, pady=5)

    # ---------- DATE FROM ----------
    tk.Label(filter_frame, text="From:", bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
    from_date = DateEntry(filter_frame, width=20, background=ACCENT, foreground=TEXT, borderwidth=2, date_pattern='yyyy-mm-dd')
    from_date.grid(row=0, column=3, padx=5, pady=5)

    # ---------- DATE TO ----------
    tk.Label(filter_frame, text="To:", bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(row=0, column=4, padx=5, pady=5)
    to_date = DateEntry(filter_frame, width=20, background=ACCENT, foreground=TEXT, borderwidth=2, date_pattern='yyyy-mm-dd')
    to_date.grid(row=0, column=5, padx=5, pady=5)

    # ---------- REPORT TYPE ----------
    tk.Label(filter_frame, text="Report Type:", bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(row=0, column=6, padx=5, pady=5)
    report_type_cb = ttk.Combobox(filter_frame, values=["Attendance","Performance","Summary"], state="readonly", width=18)
    report_type_cb.grid(row=0, column=7, padx=5, pady=5)
    report_type_cb.current(0)

    # ---------- GENERATE BUTTON ----------
    generate_btn = tk.Button(filter_frame, text="Generate", bg=ACCENT, fg=TEXT, font=("Segoe UI", 10, "bold"), relief="flat")
    generate_btn.grid(row=0, column=8, padx=10, pady=5)

    # ---------------- SUMMARY CARDS ----------------
    card_frame = tk.Frame(main, bg=BG)
    card_frame.pack(fill="x", pady=(0,15))

    total_sessions_var = tk.StringVar(value="0")
    attendance_var = tk.StringVar(value="0%")
    status_var = tk.StringVar(value="0 Completed / 0 Sessions")

    # Card helper
    def create_card(parent, text, variable):
        card = tk.Frame(parent, bg=CARD, padx=20, pady=10)
        tk.Label(card, text=text, bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).pack()
        tk.Label(card, textvariable=variable, bg=CARD, fg=TEXT, font=("Segoe UI", 14, "bold")).pack()
        return card

    c1 = create_card(card_frame, "Total Sessions", total_sessions_var)
    c2 = create_card(card_frame, "Attendance %", attendance_var)
    c3 = create_card(card_frame, "Status", status_var)

    c1.pack(side="left", padx=10)
    c2.pack(side="left", padx=10)
    c3.pack(side="left", padx=10)

    # ---------------- REPORT TABLE ----------------
    table_frame = tk.Frame(main, bg=BG)
    table_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(table_frame, show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- TREEVIEW STYLE ----------
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=CARD, foreground=TEXT, rowheight=28, fieldbackground=CARD)
    style.configure("Treeview.Heading", background=ACCENT, foreground=TEXT, font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", ACCENT)])

    # ---------------- LOAD MEMBERS ----------------
    def load_members():
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT member_id, name FROM members WHERE trainer_id=%s AND status='Active'", (trainer_id,))
            members = cursor.fetchall()
            member_cb["values"] = [f"{m['member_id']} - {m['name']}" for m in members]
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- LOAD REPORT TABLE ----------------
    def load_report_table():
        selection = member_cb.get()
        if not selection:
            messagebox.showerror("Error", "Please select a member")
            return
        member_id = int(selection.split(" - ")[0])
        from_d = from_date.get_date()
        to_d = to_date.get_date()
        rtype = report_type_cb.get()

        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if rtype == "Attendance":
                cursor.execute("""
                    SELECT date, check_in, check_out, status
                    FROM attendance
                    WHERE user_id=%s AND role='Member' AND date BETWEEN %s AND %s
                """, (member_id, from_d, to_d))

                tree["columns"] = ("date","check_in","check_out","status")
                for col, txt in zip(tree["columns"], ["Date","Check-in","Check-out","Status"]):
                    tree.heading(col, text=txt)
                    tree.column(col, anchor="center", width=120)

                for r in cursor.fetchall():
                    tree.insert("", "end", values=(r["date"], r["check_in"] or "", r["check_out"] or "", r["status"]))

            elif rtype == "Performance":
                cursor.execute("""
                    SELECT appointment_date, appointment_type, start_time, end_time, status, notes
                    FROM appointments
                    WHERE member_id=%s AND trainer_id=%s AND appointment_date BETWEEN %s AND %s
                """, (member_id, trainer_id, from_d, to_d))

                tree["columns"] = ("date","activity","start_time","end_time","status","notes")
                for col, txt in zip(tree["columns"], ["Date","Activity","Start Time","End Time","Status","Notes"]):
                    tree.heading(col, text=txt)
                    tree.column(col, anchor="center", width=120)

                for r in cursor.fetchall():
                    tree.insert("", "end", values=(r["appointment_date"], r["appointment_type"],
                                                   r["start_time"] or "", r["end_time"] or "",
                                                   r["status"], r["notes"]))

            elif rtype == "Summary":
                # Appointment summary
                cursor.execute("""
                    SELECT COUNT(*) AS total_sessions,
                           SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) AS completed,
                           SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END) AS pending,
                           SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) AS cancelled
                    FROM appointments
                    WHERE member_id=%s AND trainer_id=%s AND appointment_date BETWEEN %s AND %s
                """, (member_id, trainer_id, from_d, to_d))
                appt_summary = cursor.fetchone()

                # Attendance summary
                cursor.execute("""
                    SELECT COUNT(*) AS total_days,
                           SUM(CASE WHEN check_in IS NOT NULL THEN 1 ELSE 0 END) AS present
                    FROM attendance
                    WHERE user_id=%s AND role='Member' AND date BETWEEN %s AND %s
                """, (member_id, from_d, to_d))
                att_summary = cursor.fetchone()
                attendance_pct = 0
                if att_summary and att_summary["total_days"]:
                    attendance_pct = int(att_summary["present"]/att_summary["total_days"]*100)

                # Update cards
                total_sessions_var.set(appt_summary["total_sessions"] if appt_summary else 0)
                attendance_var.set(f"{attendance_pct}%")
                status_var.set(f"{appt_summary['completed']} Completed / {appt_summary['total_sessions']} Sessions" if appt_summary else "N/A")

                # Fill treeview
                tree["columns"] = ("metric","value")
                for col, txt in zip(tree["columns"], ["Metric","Value"]):
                    tree.heading(col, text=txt)
                    tree.column(col, anchor="center", width=200)

                summary_data = [
                    ("Total Sessions", appt_summary["total_sessions"] if appt_summary else 0),
                    ("Completed Sessions", appt_summary["completed"] if appt_summary else 0),
                    ("Pending Sessions", appt_summary["pending"] if appt_summary else 0),
                    ("Cancelled Sessions", appt_summary["cancelled"] if appt_summary else 0),
                    ("Attendance %", f"{attendance_pct}%")
                ]
                for metric, val in summary_data:
                    tree.insert("", "end", values=(metric, val))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- EXPORT FUNCTIONS ----------------
    def export_excel():
        rows = [tree.item(r)["values"] for r in tree.get_children()]
        if not rows:
            messagebox.showerror("Error", "No data to export")
            return
        df = pd.DataFrame(rows, columns=[c for c in tree["columns"]])
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if path:
            df.to_excel(path, index=False)
            messagebox.showinfo("Success", f"Report saved to {path}")

    def export_pdf():
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Error", "fpdf library not installed. Run 'pip install fpdf'")
            return
        rows = [tree.item(r)["values"] for r in tree.get_children()]
        if not rows:
            messagebox.showerror("Error", "No data to export")
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        for col in tree["columns"]:
            pdf.cell(40, 10, col, 1)
        pdf.ln()
        pdf.set_font("Arial", "", 10)
        for r in rows:
            for val in r:
                pdf.cell(40, 10, str(val), 1)
            pdf.ln()
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if path:
            pdf.output(path)
            messagebox.showinfo("Success", f"Report saved to {path}")

    # ---------- EXPORT BUTTONS ----------
    export_frame = tk.Frame(main, bg=BG)
    export_frame.pack(fill="x", pady=(10,0))
    tk.Button(export_frame, text="Export Excel", bg=ACCENT, fg=TEXT, relief="flat", command=export_excel).pack(side="left", padx=10)
    tk.Button(export_frame, text="Export PDF", bg=ACCENT, fg=TEXT, relief="flat", command=export_pdf).pack(side="left", padx=10)

    # ---------- BIND GENERATE BUTTON ----------
    generate_btn.config(command=load_report_table)

    # Load members initially
    load_members()
