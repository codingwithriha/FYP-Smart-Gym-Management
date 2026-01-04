import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database_db import get_connection
import openpyxl
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ---------------- THEME ---------------- #
PRIMARY = "#7c5dfa"
BG = "#1e1e2f"
TEXT = "#eaeaff"
ENTRY = "#22265a"

# ========================================================= #
def load_manage_appointments(parent):

    for w in parent.winfo_children():
        w.destroy()
    parent.configure(bg=BG)

    # ---------------- STYLE ---------------- #
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=ENTRY,
        foreground=TEXT,
        fieldbackground=ENTRY,
        rowheight=28,
        font=("Arial", 10)
    )

    style.configure(
        "Treeview.Heading",
        background=PRIMARY,
        foreground="white",
        font=("Arial", 10, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", PRIMARY)],
        foreground=[("selected", "white")]
    )

    # ---------------- HEADER ---------------- #
    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x", pady=(0, 10))

    tk.Label(
        header, text="Manage Appointments",
        font=("Arial", 22, "bold"),
        fg=TEXT, bg=BG
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Search appointments or filter by status",
        font=("Arial", 10),
        fg="#9fa1d6", bg=BG
    ).pack(anchor="w")

    # ---------------- FILTER / SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", padx=20, pady=8)

    tk.Label(filter_frame, text="Search by Member ID", bg=BG, fg=TEXT)\
        .grid(row=0, column=0, padx=5)

    search_var = tk.StringVar()
    tk.Entry(
        filter_frame,
        textvariable=search_var,
        bg=ENTRY, fg=TEXT,
        insertbackground=TEXT
    ).grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Filter by Status", bg=BG, fg=TEXT)\
        .grid(row=0, column=2, padx=10)

    status_filter = tk.StringVar(value="All")
    ttk.Combobox(
        filter_frame,
        state="readonly",
        values=["All", "Scheduled", "Pending", "Cancelled", "Completed"],
        textvariable=status_filter,
        width=14
    ).grid(row=0, column=3)

    # ---------------- BUTTON FRAME ---------------- #
    btn_frame = tk.Frame(parent, bg=BG)
    btn_frame.pack(fill="x", padx=20, pady=5)

    def btn(txt, color, cmd):
        return tk.Button(
            btn_frame,
            text=txt,
            bg=color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            command=cmd
        )

    # ---------------- TREEVIEW ---------------- #
    cols = (
        "Appointment ID",
        "Member ID",
        "Trainer ID",
        "Date",
        "Time Slot",
        "Notes",
        "Type",
        "Status",
        "Cancel Reason",
        "Cancelled By",
        "Cancelled At"
    )

    tree = ttk.Treeview(parent, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=130)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- FETCH DATA ---------------- #
    def fetch_appointments():
        search = search_var.get().strip().lower()
        status = status_filter.get()

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT appointment_id, member_id, trainer_id,
                       appointment_date, time_slot, notes,
                       appointment_type, status,
                       cancel_reason, cancelled_by, cancelled_at
                FROM appointments
            """)
            rows = cur.fetchall()
            con.close()

            tree.delete(*tree.get_children())
            for r in rows:
                if status != "All" and r[7] != status:
                    continue
                if search and search not in str(r[1]).lower():
                    continue
                tree.insert("", "end", values=r)

        except Exception as e:
            messagebox.showerror("Error", e)

    search_var.trace_add("write", lambda *a: fetch_appointments())
    status_filter.trace_add("write", lambda *a: fetch_appointments())

    # ---------------- FORM ---------------- #
    def open_form(update=False):
        selected = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error", "Select an appointment first")
                return
            selected = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Appointment Form")
        win.configure(bg=BG)
        win.geometry("520x650")

        fields = {}

        def entry(lbl, r):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT)\
                .grid(row=r, column=0, padx=20, pady=6, sticky="w")
            e = tk.Entry(win, bg=ENTRY, fg=TEXT, insertbackground=TEXT)
            e.grid(row=r, column=1, pady=6)
            return e

        def combo(lbl, r, values):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT)\
                .grid(row=r, column=0, padx=20, pady=6, sticky="w")
            c = ttk.Combobox(win, state="readonly", values=values)
            c.grid(row=r, column=1, pady=6)
            return c

        fields["Member ID"] = entry("Member ID", 0)
        fields["Trainer ID"] = entry("Trainer ID", 1)
        fields["Date"] = entry("Appointment Date (YYYY-MM-DD)", 2)
        fields["Time Slot"] = entry("Time Slot", 3)
        fields["Notes"] = entry("Notes", 4)
        fields["Type"] = entry("Appointment Type", 5)
        fields["Status"] = combo("Status", 6,
                                 ["Scheduled", "Pending", "Cancelled", "Completed"])
        fields["Cancel Reason"] = entry("Cancel Reason", 7)
        fields["Cancelled By"] = entry("Cancelled By", 8)
        fields["Cancelled At"] = entry("Cancelled At", 9)

        if update:
            fields["Member ID"].insert(0, selected[1])
            fields["Trainer ID"].insert(0, selected[2])
            fields["Date"].insert(0, selected[3])
            fields["Time Slot"].insert(0, selected[4])
            fields["Notes"].insert(0, selected[5])
            fields["Type"].insert(0, selected[6])
            fields["Status"].set(selected[7])
            fields["Cancel Reason"].insert(0, selected[8])
            fields["Cancelled By"].insert(0, selected[9])
            fields["Cancelled At"].insert(0, selected[10])

        def save():
            try:
                con = get_connection()
                cur = con.cursor()

                data = (
                    fields["Member ID"].get(),
                    fields["Trainer ID"].get(),
                    fields["Date"].get(),
                    fields["Time Slot"].get(),
                    fields["Notes"].get(),
                    fields["Type"].get(),
                    fields["Status"].get(),
                    fields["Cancel Reason"].get(),
                    fields["Cancelled By"].get(),
                    fields["Cancelled At"].get()
                )

                if update:
                    cur.execute("""
                        UPDATE appointments SET
                        member_id=%s, trainer_id=%s,
                        appointment_date=%s, time_slot=%s,
                        notes=%s, appointment_type=%s,
                        status=%s, cancel_reason=%s,
                        cancelled_by=%s, cancelled_at=%s
                        WHERE appointment_id=%s
                    """, data + (selected[0],))
                else:
                    cur.execute("""
                        INSERT INTO appointments
                        (member_id, trainer_id, appointment_date,
                         time_slot, notes, appointment_type,
                         status, cancel_reason, cancelled_by, cancelled_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, data)

                con.commit()
                con.close()
                win.destroy()
                fetch_appointments()

            except Exception as e:
                messagebox.showerror("Error", e)

        tk.Button(
            win, text="Save",
            bg=PRIMARY, fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).grid(row=20, columnspan=2, pady=20)

    # ---------------- DELETE ---------------- #
    def delete_appointment():
        if not tree.selection():
            return
        aid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm", "Delete selected appointment?"):
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM appointments WHERE appointment_id=%s", (aid,))
            con.commit()
            con.close()
            fetch_appointments()
        except Exception as e:
            messagebox.showerror("Error", e)

    # ---------------- REPORTS ---------------- #
    def export_excel():
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not path:
            return
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(cols)
        for i in tree.get_children():
            ws.append(tree.item(i)["values"])
        wb.save(path)
        messagebox.showinfo("Success", "Excel saved successfully")

    def export_pdf():
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not path:
            return
        data = [cols]
        for i in tree.get_children():
            data.append(tree.item(i)["values"])

        pdf = SimpleDocTemplate(path)
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor(PRIMARY)),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.black)
        ]))
        pdf.build([table])
        messagebox.showinfo("Success", "PDF saved successfully")

    # ---------------- BUTTONS ---------------- #
    btn("Add Appointment", PRIMARY, lambda: open_form()).pack(side="left", padx=5)
    btn("Update Appointment", "#0984e3", lambda: open_form(True)).pack(side="left", padx=5)
    btn("Delete", "#d63031", delete_appointment).pack(side="left", padx=5)
    btn("Excel Report", "#00b894", export_excel).pack(side="left", padx=5)
    btn("PDF Report", "#6c5ce7", export_pdf).pack(side="left", padx=5)
    btn("Refresh", "#636e72", fetch_appointments).pack(side="left", padx=5)

    fetch_appointments()
