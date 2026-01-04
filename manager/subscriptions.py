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
def load_manage_subscriptions(parent):

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
        header, text="Manage Subscriptions",
        font=("Arial", 22, "bold"),
        fg=TEXT, bg=BG
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Search subscriptions or filter by status",
        font=("Arial", 10),
        fg="#9fa1d6", bg=BG
    ).pack(anchor="w")

    # ---------------- FILTER / SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", padx=20, pady=8)

    tk.Label(filter_frame, text="Search by Member ID", bg=BG, fg=TEXT).grid(row=0, column=0, padx=5)
    search_var = tk.StringVar()
    tk.Entry(filter_frame, textvariable=search_var, bg=ENTRY, fg=TEXT, insertbackground=TEXT).grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Filter by Status", bg=BG, fg=TEXT).grid(row=0, column=2, padx=10)
    status_filter = tk.StringVar(value="All")
    ttk.Combobox(
        filter_frame,
        state="readonly",
        values=["All", "Active", "Inactive"],
        textvariable=status_filter,
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
        "Subscription ID", "Member ID", "Plan Name", "Start Date", "End Date",
        "Amount Paid", "Total Amount", "Status", "Created At"
    )

    tree = ttk.Treeview(parent, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=130)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- FETCH DATA ---------------- #
    def fetch_subscriptions():
        search = search_var.get().strip().lower()
        status = status_filter.get()

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT subscription_id, member_id, plan_name, start_date, end_date,
                       amount_paid, total_amount, status, created_at
                FROM subscriptions
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

    search_var.trace_add("write", lambda *a: fetch_subscriptions())
    status_filter.trace_add("write", lambda *a: fetch_subscriptions())

    # ---------------- FORM ---------------- #
    def open_form(update=False):
        selected = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error", "Select a subscription first")
                return
            selected = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Subscription Form")
        win.configure(bg=BG)
        win.geometry("500x600")

        fields = {}

        def entry(lbl, r):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT).grid(row=r, column=0, padx=20, pady=6, sticky="w")
            e = tk.Entry(win, bg=ENTRY, fg=TEXT, insertbackground=TEXT)
            e.grid(row=r, column=1, pady=6)
            return e

        def combo(lbl, r, values):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT).grid(row=r, column=0, padx=20, pady=6, sticky="w")
            c = ttk.Combobox(win, state="readonly", values=values)
            c.grid(row=r, column=1, pady=6)
            return c

        fields["Member ID"] = entry("Member ID", 0)
        fields["Plan Name"] = entry("Plan Name", 1)
        fields["Start Date"] = entry("Start Date (YYYY-MM-DD)", 2)
        fields["End Date"] = entry("End Date (YYYY-MM-DD)", 3)
        fields["Amount Paid"] = entry("Amount Paid", 4)
        fields["Total Amount"] = entry("Total Amount", 5)
        fields["Status"] = combo("Status", 6, ["Active", "Inactive"])
        fields["Created At"] = entry("Created At (YYYY-MM-DD HH:MM:SS)", 7)

        if update:
            for i, key in enumerate(fields):
                fields[key].insert(0, selected[i+1] if key != "Status" else selected[7])
            fields["Status"].set(selected[7])

        def save():
            try:
                con = get_connection()
                cur = con.cursor()

                data = (
                    fields["Member ID"].get(),
                    fields["Plan Name"].get(),
                    fields["Start Date"].get(),
                    fields["End Date"].get(),
                    fields["Amount Paid"].get(),
                    fields["Total Amount"].get(),
                    fields["Status"].get(),
                    fields["Created At"].get()
                )

                if update:
                    cur.execute("""
                        UPDATE subscriptions SET
                        member_id=%s, plan_name=%s, start_date=%s, end_date=%s,
                        amount_paid=%s, total_amount=%s, status=%s, created_at=%s
                        WHERE subscription_id=%s
                    """, data + (selected[0],))
                else:
                    cur.execute("""
                        INSERT INTO subscriptions
                        (member_id, plan_name, start_date, end_date,
                         amount_paid, total_amount, status, created_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, data)

                con.commit()
                con.close()
                win.destroy()
                fetch_subscriptions()

            except Exception as e:
                messagebox.showerror("Error", e)

        tk.Button(win, text="Save", bg=PRIMARY, fg="white",
                  font=("Arial", 10, "bold"), command=save).grid(row=15, columnspan=2, pady=20)

    # ---------------- DELETE ---------------- #
    def delete_subscription():
        if not tree.selection():
            return
        sid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm", "Delete selected subscription?"):
            return
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM subscriptions WHERE subscription_id=%s", (sid,))
            con.commit()
            con.close()
            fetch_subscriptions()
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
    btn("Add Subscription", PRIMARY, lambda: open_form()).pack(side="left", padx=5)
    btn("Update Subscription", "#0984e3", lambda: open_form(True)).pack(side="left", padx=5)
    btn("Delete", "#d63031", delete_subscription).pack(side="left", padx=5)
    btn("Excel Report", "#00b894", export_excel).pack(side="left", padx=5)
    btn("PDF Report", "#6c5ce7", export_pdf).pack(side="left", padx=5)
    btn("Refresh", "#636e72", fetch_subscriptions).pack(side="left", padx=5)

    fetch_subscriptions()
