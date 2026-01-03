import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database_db import get_connection
import openpyxl
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# ---------------- COLORS ---------------- #
PRIMARY = "#7c5dfa"     # main highlight color
BG = "#1e1e2f"          # dark background
TEXT = "#eaeaff"        # main text
ENTRY = "#22265a"       # input background
BTN = "#333652"          # button background

def load_manage_members(parent):
    # -------- Clear previous content --------
    for widget in parent.winfo_children():
        widget.destroy()
    parent.configure(bg=BG)

    # ---------------- STYLE ---------------- #
    style = ttk.Style()
    style.theme_use('clam')  # use clam for better color control
    style.configure("Treeview",
                    background=ENTRY,
                    foreground=TEXT,
                    fieldbackground=ENTRY,
                    rowheight=28,
                    font=("Arial", 10))
    style.configure("Treeview.Heading",
                    background=PRIMARY,
                    foreground="white",
                    font=("Arial", 10, "bold"))
    style.map("Treeview",
              background=[('selected', PRIMARY)],
              foreground=[('selected', 'white')])

    # ---------------- HEADER ---------------- #
    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x", pady=(0, 10))
    tk.Label(header, text="Manage Members", font=("Arial", 22, "bold"),
             fg=TEXT, bg=BG).pack(anchor="w")
    tk.Label(header, text="Search members by name or filter by status",
             font=("Arial", 10), fg="#8f8fb3", bg=BG).pack(anchor="w")

    # ---------------- FILTER & SEARCH ---------------- #
    filter_frame = tk.Frame(parent, bg=BG)
    filter_frame.pack(fill="x", pady=(5,10), padx=20)

    tk.Label(filter_frame, text="Search by Name:", bg=BG, fg=TEXT).grid(row=0,column=0, padx=5)
    search_var = tk.StringVar()
    search_entry = tk.Entry(filter_frame, textvariable=search_var, bg=ENTRY, fg=TEXT, insertbackground=TEXT)
    search_entry.grid(row=0,column=1, padx=5)

    tk.Label(filter_frame, text="Filter by Status:", bg=BG, fg=TEXT).grid(row=0,column=2, padx=5)
    status_var = tk.StringVar()
    status_cb = ttk.Combobox(filter_frame, textvariable=status_var, state="readonly", width=12)
    status_cb['values'] = ["All", "Active", "Inactive"]
    status_cb.current(0)
    status_cb.grid(row=0,column=3, padx=5)

    # ---------------- BUTTONS ---------------- #
    btn_frame = tk.Frame(parent, bg=BG)
    btn_frame.pack(fill="x", pady=5, padx=20)

    # ---------------- TREEVIEW ---------------- #
    cols = ("ID","Name","Password","Email","Emergency Contact","Membership Type",
            "Gym","Start Date","End Date","Status","Zone","Trainer")
    tree = ttk.Treeview(parent, columns=cols, show="headings")

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=100)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # ---------------- DB HELPERS ---------------- #
    def fetch_members():
        search_text = search_var.get().strip().lower()
        status_filter = status_var.get()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT member_id, name, password, email, emergency_contact, membership_type,
                       gym_id, membership_start_date, membership_end_date, status,
                       zone_id, trainer_id
                FROM members
            """)
            rows = cur.fetchall()
            conn.close()

            # -------- APPLY FILTER & SEARCH --------
            filtered = []
            for r in rows:
                match = True
                if status_filter != "All" and r[9] != status_filter:
                    match = False
                if search_text and search_text not in str(r[1]).lower():
                    match = False
                if match:
                    filtered.append(r)

            tree.delete(*tree.get_children())
            for r in filtered:
                tree.insert("", "end", values=r)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch members:\n{e}")

    search_var.trace_add("write", lambda *args: fetch_members())
    status_var.trace_add("write", lambda *args: fetch_members())

    # ---------------- FORM POPUP ---------------- #
    def open_form(update=False):
        sel = None
        if update:
            if not tree.selection():
                messagebox.showerror("Error","Select a member first")
                return
            sel = tree.item(tree.selection())["values"]

        win = tk.Toplevel(parent)
        win.title("Member Form")
        win.configure(bg=BG)
        win.geometry("450x650")

        fields = {}

        def add_field(lbl, row):
            tk.Label(win, text=lbl, bg=BG, fg=TEXT).grid(row=row, column=0, pady=6, sticky="w", padx=20)
            e = tk.Entry(win, bg=ENTRY, fg=TEXT, insertbackground=TEXT)
            e.grid(row=row, column=1, pady=6)
            return e

        fields["name"] = add_field("Name",0)
        fields["password"] = add_field("Password",1)
        fields["email"] = add_field("Email",2)
        fields["emergency_contact"] = add_field("Emergency Contact",3)

        def combo(lbl, row, data):
            tk.Label(win,text=lbl,bg=BG,fg=TEXT).grid(row=row,column=0,sticky="w",padx=20)
            c = ttk.Combobox(win, values=data, state="readonly")
            c.grid(row=row,column=1,pady=6)
            return c

        membership_types = ["REGULAR", "PREMIUM", "TRIAL"]
        status_list = ["Active","Inactive"]

        fields["membership_type"] = combo("Membership Type",4,membership_types)
        fields["gym"] = add_field("Gym",5)
        fields["start_date"] = add_field("Start Date (YYYY-MM-DD)",6)
        fields["end_date"] = add_field("End Date (YYYY-MM-DD)",7)
        fields["status"] = combo("Status",8,status_list)
        fields["zone"] = add_field("Zone",9)
        fields["trainer"] = add_field("Trainer",10)

        if update:
            fields["name"].insert(0, sel[1])
            fields["password"].insert(0, sel[2])
            fields["email"].insert(0, sel[3])
            fields["emergency_contact"].insert(0, sel[4])
            fields["membership_type"].set(sel[5])
            fields["gym"].insert(0, sel[6])
            fields["start_date"].insert(0, sel[7])
            fields["end_date"].insert(0, sel[8])
            fields["status"].set(sel[9])
            fields["zone"].insert(0, sel[10])
            fields["trainer"].insert(0, sel[11])

        def save():
            try:
                conn = get_connection()
                cur = conn.cursor()
                if update:
                    cur.execute("""
                        UPDATE members SET
                        name=%s, password=%s, email=%s, emergency_contact=%s,
                        membership_type=%s, gym_id=%s,
                        membership_start_date=%s, membership_end_date=%s,
                        status=%s, zone_id=%s, trainer_id=%s
                        WHERE member_id=%s
                    """,(
                        fields["name"].get(), fields["password"].get(), fields["email"].get(),
                        fields["emergency_contact"].get(), fields["membership_type"].get(),
                        fields["gym"].get(), fields["start_date"].get(), fields["end_date"].get(),
                        fields["status"].get(), fields["zone"].get(), fields["trainer"].get(),
                        sel[0] if sel else None
                    ))
                else:
                    cur.execute("""
                        INSERT INTO members
                        (name, password, email, emergency_contact, membership_type,
                         gym_id, membership_start_date, membership_end_date,
                         status, zone_id, trainer_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,(
                        fields["name"].get(), fields["password"].get(), fields["email"].get(),
                        fields["emergency_contact"].get(), fields["membership_type"].get(),
                        fields["gym"].get(), fields["start_date"].get(), fields["end_date"].get(),
                        fields["status"].get(), fields["zone"].get(), fields["trainer"].get()
                    ))
                conn.commit()
                conn.close()
                win.destroy()
                fetch_members()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save member:\n{e}")

        tk.Button(win,text="Save",bg=PRIMARY,fg="white",
                  font=("Arial",10,"bold"),command=save).grid(row=11,columnspan=2,pady=20)

    # ---------------- DELETE ---------------- #
    def delete_member():
        if not tree.selection():
            return
        mid = tree.item(tree.selection())["values"][0]
        if not messagebox.askyesno("Confirm","Delete member and related records?"):
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM attendance WHERE user_id=%s",(mid,))
            cur.execute("DELETE FROM members WHERE member_id=%s",(mid,))
            conn.commit()
            conn.close()
            fetch_members()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete member:\n{e}")

    # ---------------- REPORTS ---------------- #
    def export_excel():
        try:
            path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel Files","*.xlsx")])
            if not path:
                return
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(cols)
            for r in tree.get_children():
                ws.append(tree.item(r)["values"])
            wb.save(path)
            messagebox.showinfo("Done","Excel report saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Excel:\n{e}")

    def export_pdf():
        try:
            path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF Files","*.pdf")])
            if not path:
                return
            data = [cols]
            for r in tree.get_children():
                data.append(tree.item(r)["values"])
            pdf = SimpleDocTemplate(path)
            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor(PRIMARY)),
                ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("GRID",(0,0),(-1,-1),1,colors.black)
            ]))
            pdf.build([table])
            messagebox.showinfo("Done","PDF report saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{e}")

    # ---------------- BUTTONS ---------------- #
    styled_btn = lambda text,color,cmd: tk.Button(btn_frame, text=text, bg=color, fg="white",
                                                  font=("Arial",10,"bold"), relief="flat",
                                                  padx=12, pady=6, command=cmd)

    styled_btn("Add Member", PRIMARY, lambda: open_form()).pack(side="left", padx=5)
    styled_btn("Update Member", "#7c5dfa", lambda: open_form(True)).pack(side="left", padx=5)
    styled_btn("Delete Selected", "#7c5dfa", lambda: delete_member()).pack(side="left", padx=5)
    styled_btn("Excel Report", "#7c5dfa", lambda: export_excel()).pack(side="left", padx=5)
    styled_btn("PDF Report", "#7c5dfa", lambda: export_pdf()).pack(side="left", padx=5)
    styled_btn("Refresh", "#7c5dfa", lambda: fetch_members()).pack(side="left", padx=5)

    fetch_members()
