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
def load_manage_messages(parent):

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
        header, text="Manage Messages",
        font=("Arial", 22, "bold"),
        fg=TEXT, bg=BG
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Search by Sender ID, Receiver ID or Status",
        font=("Arial", 10),
        fg="#9fa1d6", bg=BG
    ).pack(anchor="w")

    # ---------------- FILTER / SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", padx=20, pady=8)

    tk.Label(filter_frame, text="Search", bg=BG, fg=TEXT).grid(row=0, column=0, padx=5)
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
        "ID", "Sender ID", "Receiver ID", "User ID",
        "Branch", "City", "Area",
        "Message", "Created At", "Status"
    )

    tree = ttk.Treeview(parent, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=130)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- FETCH DATA ---------------- #
    def fetch_messages():
        search = (search_var.get() or "").lower()

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT id, sender_id, receiver_id, user_id,
                       branch, city, area, message, created_at, status
                FROM messages
                ORDER BY created_at DESC
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

    search_var.trace_add("write", lambda *a: fetch_messages())

    # ---------------- FORM ---------------- #
    def open_form(update=False):
        selected = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error", "Select a message first")
                return
            selected = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Message Form")
        win.configure(bg=BG)
        win.geometry("520x550")

        fields = {}

        def entry(lbl, r):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT)\
                .grid(row=r, column=0, padx=20, pady=6, sticky="w")
            e = tk.Entry(win, bg=ENTRY, fg=TEXT, insertbackground=TEXT, width=35)
            e.grid(row=r, column=1, pady=6)
            return e

        fields["Sender ID"] = entry("Sender ID", 0)
        fields["Receiver ID"] = entry("Receiver ID", 1)
        fields["User ID"] = entry("User ID", 2)
        fields["Branch"] = entry("Branch", 3)
        fields["City"] = entry("City", 4)
        fields["Area"] = entry("Area", 5)
        fields["Message"] = entry("Message", 6)
        fields["Status"] = entry("Status", 7)

        if update:
            keys = list(fields.keys())
            for i, k in enumerate(keys):
                fields[k].insert(0, selected[i+1])

        def save():
            try:
                con = get_connection()
                cur = con.cursor()

                data = tuple(f.get() for f in fields.values())

                if update:
                    cur.execute("""
                        UPDATE messages SET
                        sender_id=%s, receiver_id=%s, user_id=%s,
                        branch=%s, city=%s, area=%s,
                        message=%s, status=%s
                        WHERE id=%s
                    """, data + (selected[0],))
                else:
                    cur.execute("""
                        INSERT INTO messages
                        (sender_id, receiver_id, user_id, branch,
                         city, area, message, status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, data)

                con.commit()
                con.close()
                win.destroy()
                fetch_messages()

            except Exception as e:
                messagebox.showerror("Error", e)

        tk.Button(
            win, text="Save",
            bg=PRIMARY, fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).grid(row=12, columnspan=2, pady=20)

    # ---------------- DELETE ---------------- #
    def delete_message():
        if not tree.selection():
            return
        mid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm", "Delete selected message?"):
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM messages WHERE id=%s", (mid,))
            con.commit()
            con.close()
            fetch_messages()
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
        messagebox.showinfo("Success", "Excel report saved")

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
        messagebox.showinfo("Success", "PDF report saved")

    # ---------------- BUTTONS ---------------- #
    btn("Delete", "#d63031", delete_message).pack(side="left", padx=5)
    btn("Excel Report", "#00b894", export_excel).pack(side="left", padx=5)
    btn("PDF Report", "#6c5ce7", export_pdf).pack(side="left", padx=5)
    btn("Refresh", "#636e72", fetch_messages).pack(side="left", padx=5)

    fetch_messages()
