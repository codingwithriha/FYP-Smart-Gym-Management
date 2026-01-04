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
def load_manage_attendance(parent):

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
        header, text="Manage Attendance",
        font=("Arial", 22, "bold"),
        fg=TEXT, bg=BG
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Search attendance or filter by role",
        font=("Arial", 10),
        fg="#9fa1d6", bg=BG
    ).pack(anchor="w")

    # ---------------- FILTER / SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", padx=20, pady=8)

    tk.Label(filter_frame, text="Search by User ID", bg=BG, fg=TEXT)\
        .grid(row=0, column=0, padx=5)

    search_var = tk.StringVar()
    tk.Entry(
        filter_frame,
        textvariable=search_var,
        bg=ENTRY, fg=TEXT,
        insertbackground=TEXT
    ).grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Filter by Role", bg=BG, fg=TEXT)\
        .grid(row=0, column=2, padx=10)

    role_filter = tk.StringVar(value="All")
    ttk.Combobox(
        filter_frame,
        state="readonly",
        values=["All", "Admin", "Manager", "Trainer", "Member"],
        textvariable=role_filter,
        width=12
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
        "Attendance ID",
        "User ID",
        "Date",
        "Check In",
        "Check Out",
        "Role",
        "Status"
    )

    tree = ttk.Treeview(parent, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=130)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- FETCH DATA ---------------- #
    def fetch_attendance():
        search = search_var.get().strip().lower()
        role = role_filter.get()

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT attendance_id, user_id, date,
                       check_in, check_out, role, status
                FROM attendance
            """)
            rows = cur.fetchall()
            con.close()

            tree.delete(*tree.get_children())
            for r in rows:
                if role != "All" and r[5] != role:
                    continue
                if search and search not in str(r[1]).lower():
                    continue
                tree.insert("", "end", values=r)

        except Exception as e:
            messagebox.showerror("Error", e)

    search_var.trace_add("write", lambda *a: fetch_attendance())
    role_filter.trace_add("write", lambda *a: fetch_attendance())

    # ---------------- FORM ---------------- #
    def open_form(update=False):
        selected = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error", "Select a record first")
                return
            selected = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Attendance Form")
        win.configure(bg=BG)
        win.geometry("420x520")

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

        fields["User ID"] = entry("User ID", 0)
        fields["Date"] = entry("Date (YYYY-MM-DD)", 1)
        fields["Check In"] = entry("Check In (HH:MM)", 2)
        fields["Check Out"] = entry("Check Out (HH:MM)", 3)
        fields["Role"] = combo("Role", 4, ["Admin","Manager","Trainer","Member"])
        fields["Status"] = combo("Status", 5, ["Active","Inactive"])

        if update:
            fields["User ID"].insert(0, selected[1])
            fields["Date"].insert(0, selected[2])
            fields["Check In"].insert(0, selected[3])
            fields["Check Out"].insert(0, selected[4])
            fields["Role"].set(selected[5])
            fields["Status"].set(selected[6])

        def save():
            try:
                con = get_connection()
                cur = con.cursor()

                data = (
                    fields["User ID"].get(),
                    fields["Date"].get(),
                    fields["Check In"].get(),
                    fields["Check Out"].get(),
                    fields["Role"].get(),
                    fields["Status"].get()
                )

                if update:
                    cur.execute("""
                        UPDATE attendance SET
                        user_id=%s, date=%s,
                        check_in=%s, check_out=%s,
                        role=%s, status=%s
                        WHERE attendance_id=%s
                    """, data + (selected[0],))
                else:
                    cur.execute("""
                        INSERT INTO attendance
                        (user_id, date, check_in, check_out, role, status)
                        VALUES (%s,%s,%s,%s,%s,%s)
                    """, data)

                con.commit()
                con.close()
                win.destroy()
                fetch_attendance()

            except Exception as e:
                messagebox.showerror("Error", e)

        tk.Button(
            win,
            text="Save",
            bg=PRIMARY,
            fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).grid(row=10, columnspan=2, pady=20)

    # ---------------- DELETE ---------------- #
    def delete_attendance():
        if not tree.selection():
            return
        aid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm", "Delete selected record?"):
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM attendance WHERE attendance_id=%s", (aid,))
            con.commit()
            con.close()
            fetch_attendance()
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
    btn("Add Attendance", PRIMARY, lambda: open_form()).pack(side="left", padx=5)
    btn("Update Attendance", "#0984e3", lambda: open_form(True)).pack(side="left", padx=5)
    btn("Delete", "#d63031", delete_attendance).pack(side="left", padx=5)
    btn("Excel Report", "#00b894", export_excel).pack(side="left", padx=5)
    btn("PDF Report", "#6c5ce7", export_pdf).pack(side="left", padx=5)
    btn("Refresh", "#636e72", fetch_attendance).pack(side="left", padx=5)

    fetch_attendance()
