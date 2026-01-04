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
def load_manage_trainers(parent):
    for w in parent.winfo_children():
        w.destroy()
    parent.configure(bg=BG)

    # ---------------- STYLE ---------------- #
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
        background=ENTRY,
        foreground=TEXT,
        fieldbackground=ENTRY,
        rowheight=28,
        font=("Arial", 10)
    )

    style.configure("Treeview.Heading",
        background=PRIMARY,
        foreground="white",
        font=("Arial", 10, "bold")
    )

    style.map("Treeview",
        background=[("selected", PRIMARY)],
        foreground=[("selected", "white")]
    )

    # ---------------- HEADER ---------------- #
    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x", pady=(0, 10))

    tk.Label(
        header, text="Manage Trainers",
        font=("Arial", 22, "bold"),
        fg=TEXT, bg=BG
    ).pack(anchor="w")

    tk.Label(
        header, text="Search by name or filter by status",
        font=("Arial", 10),
        fg="#9fa1d6",
        bg=BG
    ).pack(anchor="w")

    # ---------------- FILTER / SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", padx=20, pady=8)

    tk.Label(filter_frame, text="Search by Name", bg=BG, fg=TEXT).grid(row=0, column=0, padx=5)
    search_var = tk.StringVar()
    tk.Entry(
        filter_frame, textvariable=search_var,
        bg=ENTRY, fg=TEXT, insertbackground=TEXT
    ).grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Filter by Status", bg=BG, fg=TEXT).grid(row=0, column=2, padx=10)
    status_var = tk.StringVar(value="All")
    status_cb = ttk.Combobox(filter_frame, state="readonly",
                             values=["All", "Active", "Inactive"],
                             textvariable=status_var, width=12)
    status_cb.grid(row=0, column=3)

    # ---------------- BUTTONS ---------------- #
    btn_frame = tk.Frame(parent, bg=BG)
    btn_frame.pack(fill="x", padx=20, pady=5)

    def btn(txt, color, cmd):
        return tk.Button(
            btn_frame, text=txt, bg=color, fg="white",
            font=("Arial", 10, "bold"),
            relief="flat", padx=12, pady=6,
            command=cmd
        )

    # ---------------- TREEVIEW ---------------- #
    cols = (
        "Trainer ID", "Name", "Email", "Contact", "Password",
        "Specialization", "Qualification", "Experience Years",
        "Gym ID", "Zone ID", "Status", "Shift Time"
    )

    tree = ttk.Treeview(parent, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=110, anchor="center")

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- FETCH DATA ---------------- #
    def fetch_trainers():
        search = search_var.get().lower().strip()
        status = status_var.get()

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT trainer_id, name, email, emergency_contact, password,
                       specialization, qualification, experience_years,
                       gym_id, zone_id, status, shift_time
                FROM trainers
            """)
            rows = cur.fetchall()
            con.close()

            tree.delete(*tree.get_children())
            for r in rows:
                if status != "All" and r[10] != status:
                    continue
                if search and search not in r[1].lower():
                    continue
                tree.insert("", "end", values=r)

        except Exception as e:
            messagebox.showerror("Error", e)

    search_var.trace_add("write", lambda *a: fetch_trainers())
    status_var.trace_add("write", lambda *a: fetch_trainers())

    # ---------------- FORM ---------------- #
    def open_form(update=False):
        selected = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error", "Select a trainer first")
                return
            selected = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Trainer Form")
        win.configure(bg=BG)
        win.geometry("480x650")

        fields = {}

        def entry(lbl, r):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT).grid(row=r, column=0, padx=20, pady=6, sticky="w")
            e = tk.Entry(win, bg=ENTRY, fg=TEXT, insertbackground=TEXT)
            e.grid(row=r, column=1, pady=6)
            return e

        def combo(lbl, r):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT).grid(row=r, column=0, padx=20, pady=6, sticky="w")
            c = ttk.Combobox(win, state="readonly", values=["Active", "Inactive"])
            c.grid(row=r, column=1, pady=6)
            return c

        labels = [
            "Name","Email","Contact","Password","Specialization",
            "Qualification","Experience Years","Gym ID","Zone ID","Shift Time"
        ]

        for i, l in enumerate(labels):
            fields[l] = entry(l, i)

        fields["Status"] = combo("Status", len(labels))

        if update:
            for i, key in enumerate(fields):
                fields[key].insert(0, selected[i+1] if key != "Status" else "")
            fields["Status"].set(selected[10])

        def save():
            try:
                con = get_connection()
                cur = con.cursor()

                data = (
                    fields["Name"].get(), fields["Email"].get(),
                    fields["Contact"].get(), fields["Password"].get(),
                    fields["Specialization"].get(), fields["Qualification"].get(),
                    fields["Experience Years"].get(), fields["Gym ID"].get(),
                    fields["Zone ID"].get(), fields["Status"].get(),
                    fields["Shift Time"].get()
                )

                if update:
                    cur.execute("""
                        UPDATE trainers SET
                        name=%s,email=%s,emergency_contact=%s,password=%s,
                        specialization=%s,qualification=%s,experience_years=%s,
                        gym_id=%s,zone_id=%s,status=%s,shift_time=%s
                        WHERE trainer_id=%s
                    """, data + (selected[0],))
                else:
                    cur.execute("""
                        INSERT INTO trainers
                        (name,email,emergency_contact,password,specialization,
                         qualification,experience_years,gym_id,zone_id,status,shift_time)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, data)

                con.commit()
                con.close()
                win.destroy()
                fetch_trainers()

            except Exception as e:
                messagebox.showerror("Error", e)

        tk.Button(win, text="Save", bg=PRIMARY, fg="white",
                  font=("Arial", 10, "bold"), command=save)\
            .grid(row=20, columnspan=2, pady=20)

    # ---------------- DELETE ---------------- #
    def delete_trainer():
        if not tree.selection():
            return
        tid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm", "Delete selected trainer?"):
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM trainers WHERE trainer_id=%s", (tid,))
            con.commit()
            con.close()
            fetch_trainers()
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
    btn("Add Trainer", PRIMARY, lambda: open_form()).pack(side="left", padx=5)
    btn("Update Trainer", "#0984e3", lambda: open_form(True)).pack(side="left", padx=5)
    btn("Delete", "#d63031", delete_trainer).pack(side="left", padx=5)
    btn("Excel Report", "#00b894", export_excel).pack(side="left", padx=5)
    btn("PDF Report", "#6c5ce7", export_pdf).pack(side="left", padx=5)
    btn("Refresh", "#636e72", fetch_trainers).pack(side="left", padx=5)

    fetch_trainers()
