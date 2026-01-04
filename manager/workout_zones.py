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
def load_manage_workout_zones(parent):

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
        header, text="Manage Workout Zones",
        font=("Arial", 22, "bold"),
        fg=TEXT, bg=BG
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Search zones by Name or Type",
        font=("Arial", 10),
        fg="#9fa1d6", bg=BG
    ).pack(anchor="w")

    # ---------------- FILTER / SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", padx=20, pady=8)

    tk.Label(filter_frame, text="Search", bg=BG, fg=TEXT)\
        .grid(row=0, column=0, padx=5)

    search_var = tk.StringVar()
    tk.Entry(
        filter_frame,
        textvariable=search_var,
        bg=ENTRY, fg=TEXT,
        insertbackground=TEXT
    ).grid(row=0, column=1, padx=5)

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
        "Zone ID",
        "Zone Name",
        "Zone Type",
        "Gym ID",
        "Announcements",
        "Floor Number"
    )

    tree = ttk.Treeview(parent, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=140)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- FETCH DATA ---------------- #
    def fetch_zones():
        search = (search_var.get() or "").lower()

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT zone_id, zone_name, zone_type,
                       gym_id, announcements, floor_number
                FROM workout_zones
            """)
            rows = cur.fetchall()
            con.close()

            tree.delete(*tree.get_children())
            for r in rows:
                text = " ".join(str(x) for x in r if x)
                if search and search not in text.lower():
                    continue
                tree.insert("", "end", values=r)

        except Exception as e:
            messagebox.showerror("Error", e)

    search_var.trace_add("write", lambda *a: fetch_zones())

    # ---------------- FORM ---------------- #
    def open_form(update=False):
        selected = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error", "Select a zone first")
                return
            selected = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Workout Zone Form")
        win.configure(bg=BG)
        win.geometry("520x520")

        fields = {}

        def entry(lbl, r):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT)\
                .grid(row=r, column=0, padx=20, pady=6, sticky="w")
            e = tk.Entry(win, bg=ENTRY, fg=TEXT, insertbackground=TEXT, width=35)
            e.grid(row=r, column=1, pady=6)
            return e

        def combo(lbl, r, values):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT)\
                .grid(row=r, column=0, padx=20, pady=6, sticky="w")
            c = ttk.Combobox(win, values=values, state="readonly", width=32)
            c.grid(row=r, column=1, pady=6)
            return c

        fields["Zone Name"] = entry("Zone Name", 0)
        fields["Zone Type"] = entry("Zone Type", 1)
        fields["Gym ID"] = entry("Gym ID", 2)
        fields["Announcements"] = entry("Announcements", 3)
        fields["Floor Number"] = combo(
            "Floor Number", 4,
            ["Ground Floor", "First Floor", "Second Floor"]
        )

        if update:
            keys = list(fields.keys())
            for i, k in enumerate(keys):
                fields[k].insert(0, selected[i+1])

        def save():
            try:
                con = get_connection()
                cur = con.cursor()

                data = (
                    fields["Zone Name"].get(),
                    fields["Zone Type"].get(),
                    fields["Gym ID"].get(),
                    fields["Announcements"].get(),
                    fields["Floor Number"].get()
                )

                if update:
                    cur.execute("""
                        UPDATE workout_zones SET
                        zone_name=%s,
                        zone_type=%s,
                        gym_id=%s,
                        announcements=%s,
                        floor_number=%s
                        WHERE zone_id=%s
                    """, data + (selected[0],))
                else:
                    cur.execute("""
                        INSERT INTO workout_zones
                        (zone_name, zone_type, gym_id, announcements, floor_number)
                        VALUES (%s,%s,%s,%s,%s)
                    """, data)

                con.commit()
                con.close()
                win.destroy()
                fetch_zones()

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
    def delete_zone():
        if not tree.selection():
            return
        zid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm", "Delete selected zone?"):
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM workout_zones WHERE zone_id=%s", (zid,))
            con.commit()
            con.close()
            fetch_zones()
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
    btn("Add Zone", PRIMARY, lambda: open_form()).pack(side="left", padx=5)
    btn("Update Zone", "#0984e3", lambda: open_form(True)).pack(side="left", padx=5)
    btn("Delete", "#d63031", delete_zone).pack(side="left", padx=5)
    btn("Excel Report", "#00b894", export_excel).pack(side="left", padx=5)
    btn("PDF Report", "#6c5ce7", export_pdf).pack(side="left", padx=5)
    btn("Refresh", "#636e72", fetch_zones).pack(side="left", padx=5)

    fetch_zones()
