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
def load_manage_announcements(parent):

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
        header, text="Manage Announcements",
        font=("Arial", 22, "bold"),
        fg=TEXT, bg=BG
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Search announcements by Title or Message",
        font=("Arial", 10),
        fg="#9fa1d6", bg=BG
    ).pack(anchor="w")

    # ---------------- FILTER / SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", padx=20, pady=8)

    tk.Label(filter_frame, text="Search by Title / Message", bg=BG, fg=TEXT).grid(row=0, column=0, padx=5)
    search_var = tk.StringVar()
    tk.Entry(filter_frame, textvariable=search_var, bg=ENTRY, fg=TEXT, insertbackground=TEXT).grid(row=0, column=1, padx=5)

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
    cols = ("Announcement ID", "Title", "Message", "Created At")

    tree = ttk.Treeview(parent, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=150)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- FETCH DATA ---------------- #
    def fetch_announcements():
        search = search_var.get().strip().lower()

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT announcement_id, title, message, created_at
                FROM announcements
            """)
            rows = cur.fetchall()
            con.close()

            tree.delete(*tree.get_children())
            for r in rows:
                if search and search not in str(r[1]).lower() and search not in str(r[2]).lower():
                    continue
                tree.insert("", "end", values=r)

        except Exception as e:
            messagebox.showerror("Error", e)

    search_var.trace_add("write", lambda *a: fetch_announcements())

    # ---------------- FORM ---------------- #
    def open_form(update=False):
        selected = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error", "Select an announcement first")
                return
            selected = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Announcement Form")
        win.configure(bg=BG)
        win.geometry("500x450")

        fields = {}

        def entry(lbl, r):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT).grid(row=r, column=0, padx=20, pady=6, sticky="w")
            e = tk.Entry(win, bg=ENTRY, fg=TEXT, insertbackground=TEXT)
            e.grid(row=r, column=1, pady=6)
            return e

        fields["Title"] = entry("Title", 0)
        fields["Message"] = entry("Message", 1)
        fields["Created At"] = entry("Created At (YYYY-MM-DD)", 2)

        if update:
            for i, key in enumerate(fields):
                fields[key].insert(0, selected[i+1])

        def save():
            try:
                con = get_connection()
                cur = con.cursor()
                data = (
                    fields["Title"].get(),
                    fields["Message"].get(),
                    fields["Created At"].get()
                )

                if update:
                    cur.execute("""
                        UPDATE announcements SET
                        title=%s, message=%s, created_at=%s
                        WHERE announcement_id=%s
                    """, data + (selected[0],))
                else:
                    cur.execute("""
                        INSERT INTO announcements
                        (title, message, created_at)
                        VALUES (%s,%s,%s)
                    """, data)

                con.commit()
                con.close()
                win.destroy()
                fetch_announcements()

            except Exception as e:
                messagebox.showerror("Error", e)

        tk.Button(win, text="Save", bg=PRIMARY, fg="white",
                  font=("Arial", 10, "bold"), command=save).grid(row=10, columnspan=2, pady=20)

    # ---------------- DELETE ---------------- #
    def delete_announcement():
        if not tree.selection():
            return
        aid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm", "Delete selected announcement?"):
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM announcements WHERE announcement_id=%s", (aid,))
            con.commit()
            con.close()
            fetch_announcements()
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
    btn("Add Announcement", PRIMARY, lambda: open_form()).pack(side="left", padx=5)
    btn("Update Announcement", "#0984e3", lambda: open_form(True)).pack(side="left", padx=5)
    btn("Delete", "#d63031", delete_announcement).pack(side="left", padx=5)
    btn("Excel Report", "#00b894", export_excel).pack(side="left", padx=5)
    btn("PDF Report", "#6c5ce7", export_pdf).pack(side="left", padx=5)
    btn("Refresh", "#636e72", fetch_announcements).pack(side="left", padx=5)

    fetch_announcements()
