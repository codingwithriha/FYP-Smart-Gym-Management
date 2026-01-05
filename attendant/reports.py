import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database_db import get_connection
from datetime import datetime
import pandas as pd
from fpdf import FPDF

# ================= COLORS =================
BG = "#1e1e2f"
TAB_BG = "#2a2a3d"
PRIMARY = "#7c5dfa"
TEXT = "#ffffff"
MUTED = "#b5b5d6"

def load_reports(parent_frame, attendant_id):
    """Attendant Reports Page with Member, Trainer, and Equipment Reports"""

    # Clear previous widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # ------------------ Top Bar ------------------
    top_bar = tk.Frame(parent_frame, bg=PRIMARY, height=50)
    top_bar.pack(fill="x")
    tk.Label(top_bar, text="Reports", bg=PRIMARY, fg=TEXT,
             font=("Segoe UI", 14, "bold")).pack(expand=True)

    # ------------------ Notebook (Tabs) ------------------
    notebook = ttk.Notebook(parent_frame)
    notebook.pack(fill="both", expand=True, padx=15, pady=15)

    # ------------------ TAB 1: Member Attendance ------------------
    tab_member = tk.Frame(notebook, bg=BG)
    notebook.add(tab_member, text="Member Attendance")

    # Filters Frame
    filters_member = tk.Frame(tab_member, bg=BG)
    filters_member.pack(fill="x", pady=(10,0))

    tk.Label(filters_member, text="From (YYYY-MM-DD):", bg=BG, fg=TEXT).pack(side="left", padx=(10,0))
    from_date_mem = tk.Entry(filters_member)
    from_date_mem.pack(side="left", padx=5)
    tk.Label(filters_member, text="To (YYYY-MM-DD):", bg=BG, fg=TEXT).pack(side="left", padx=5)
    to_date_mem = tk.Entry(filters_member)
    to_date_mem.pack(side="left", padx=5)

    btn_generate_member = tk.Button(filters_member, text="Generate Report", bg=PRIMARY, fg=TEXT,
                                    font=("Segoe UI", 10, "bold"))
    btn_generate_member.pack(side="left", padx=10)

    # TreeView
    columns_member = ("Date", "Member Name", "Check-in", "Check-out", "Status")
    tree_member = ttk.Treeview(tab_member, columns=columns_member, show="headings")
    for col in columns_member:
        tree_member.heading(col, text=col)
        tree_member.column(col, anchor="center", width=120)
    tree_member.pack(fill="both", expand=True, pady=10, padx=10)

    # Export Buttons
    btn_frame_mem = tk.Frame(tab_member, bg=BG)
    btn_frame_mem.pack(fill="x", pady=(0,10), padx=10)
    btn_export_excel_mem = tk.Button(btn_frame_mem, text="Export Excel", bg=PRIMARY, fg=TEXT,
                                     font=("Segoe UI", 10, "bold"))
    btn_export_excel_mem.pack(side="left", padx=5)
    btn_export_pdf_mem = tk.Button(btn_frame_mem, text="Export PDF", bg=PRIMARY, fg=TEXT,
                                   font=("Segoe UI", 10, "bold"))
    btn_export_pdf_mem.pack(side="left", padx=5)

    # ------------------ TAB 2: Trainer Attendance ------------------
    tab_trainer = tk.Frame(notebook, bg=BG)
    notebook.add(tab_trainer, text="Trainer Attendance")

    filters_trainer = tk.Frame(tab_trainer, bg=BG)
    filters_trainer.pack(fill="x", pady=(10,0))

    tk.Label(filters_trainer, text="From (YYYY-MM-DD):", bg=BG, fg=TEXT).pack(side="left", padx=(10,0))
    from_date_tr = tk.Entry(filters_trainer)
    from_date_tr.pack(side="left", padx=5)
    tk.Label(filters_trainer, text="To (YYYY-MM-DD):", bg=BG, fg=TEXT).pack(side="left", padx=5)
    to_date_tr = tk.Entry(filters_trainer)
    to_date_tr.pack(side="left", padx=5)

    btn_generate_trainer = tk.Button(filters_trainer, text="Generate Report", bg=PRIMARY, fg=TEXT,
                                     font=("Segoe UI", 10, "bold"))
    btn_generate_trainer.pack(side="left", padx=10)

    columns_trainer = ("Date", "Trainer Name", "Check-in", "Check-out", "Status")
    tree_trainer = ttk.Treeview(tab_trainer, columns=columns_trainer, show="headings")
    for col in columns_trainer:
        tree_trainer.heading(col, text=col)
        tree_trainer.column(col, anchor="center", width=120)
    tree_trainer.pack(fill="both", expand=True, pady=10, padx=10)

    btn_frame_tr = tk.Frame(tab_trainer, bg=BG)
    btn_frame_tr.pack(fill="x", pady=(0,10), padx=10)
    btn_export_excel_tr = tk.Button(btn_frame_tr, text="Export Excel", bg=PRIMARY, fg=TEXT,
                                    font=("Segoe UI", 10, "bold"))
    btn_export_excel_tr.pack(side="left", padx=5)
    btn_export_pdf_tr = tk.Button(btn_frame_tr, text="Export PDF", bg=PRIMARY, fg=TEXT,
                                  font=("Segoe UI", 10, "bold"))
    btn_export_pdf_tr.pack(side="left", padx=5)

    # ------------------ TAB 3: Equipment Status ------------------
    tab_equipment = tk.Frame(notebook, bg=BG)
    notebook.add(tab_equipment, text="Equipment Status")

    columns_equipment = ("Equipment ID", "Name", "Quantity", "Purchase Date", "Status", "Zone ID")
    tree_equipment = ttk.Treeview(tab_equipment, columns=columns_equipment, show="headings")
    for col in columns_equipment:
        tree_equipment.heading(col, text=col)
        tree_equipment.column(col, anchor="center", width=120)
    tree_equipment.pack(fill="both", expand=True, pady=10, padx=10)

    btn_frame_eq = tk.Frame(tab_equipment, bg=BG)
    btn_frame_eq.pack(fill="x", pady=(0,10), padx=10)
    btn_export_excel_eq = tk.Button(btn_frame_eq, text="Export Excel", bg=PRIMARY, fg=TEXT,
                                    font=("Segoe UI", 10, "bold"))
    btn_export_excel_eq.pack(side="left", padx=5)
    btn_export_pdf_eq = tk.Button(btn_frame_eq, text="Export PDF", bg=PRIMARY, fg=TEXT,
                                  font=("Segoe UI", 10, "bold"))
    btn_export_pdf_eq.pack(side="left", padx=5)

    # ------------------ Functions to Load Data ------------------
    def generate_member_report():
        from_dt = from_date_mem.get()
        to_dt = to_date_mem.get()
        tree_member.delete(*tree_member.get_children())

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT a.date, m.name, a.check_in, a.check_out, a.status
            FROM attendance a
            JOIN members m ON a.user_id = m.member_id
            WHERE a.role='Member'
        """
        if from_dt.strip():
            query += f" AND a.date >= '{from_dt.strip()}'"
        if to_dt.strip():
            query += f" AND a.date <= '{to_dt.strip()}'"
        query += " ORDER BY a.date DESC"
        cursor.execute(query)
        for r in cursor.fetchall():
            tree_member.insert("", "end", values=(r["date"], r["name"], r["check_in"], r["check_out"], r["status"]))
        conn.close()

    def generate_trainer_report():
        from_dt = from_date_tr.get()
        to_dt = to_date_tr.get()
        tree_trainer.delete(*tree_trainer.get_children())

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT a.date, t.name, a.check_in, a.check_out, a.status
            FROM attendance a
            JOIN trainers t ON a.user_id = t.trainer_id
            WHERE a.role='Trainer'
        """
        if from_dt.strip():
            query += f" AND a.date >= '{from_dt.strip()}'"
        if to_dt.strip():
            query += f" AND a.date <= '{to_dt.strip()}'"
        query += " ORDER BY a.date DESC"
        cursor.execute(query)
        for r in cursor.fetchall():
            tree_trainer.insert("", "end", values=(r["date"], r["name"], r["check_in"], r["check_out"], r["status"]))
        conn.close()

    def load_equipment_status():
        tree_equipment.delete(*tree_equipment.get_children())
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT equipment_id, name, quantity, purchase_date, status, zone_id
            FROM equipment
            ORDER BY equipment_id
        """)
        for r in cursor.fetchall():
            tree_equipment.insert("", "end", values=(
                r["equipment_id"], r["name"], r["quantity"],
                r["purchase_date"].strftime("%Y-%m-%d") if r["purchase_date"] else "",
                r["status"], r["zone_id"]
            ))
        conn.close()

    # ------------------ Bind Buttons ------------------
    btn_generate_member.config(command=generate_member_report)
    btn_generate_trainer.config(command=generate_trainer_report)
    load_equipment_status()

    # ------------------ Export Functions ------------------
    def export_tree_to_excel(tree):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx")])
        if path:
            data = [tree.item(i)["values"] for i in tree.get_children()]
            df = pd.DataFrame(data, columns=[tree.heading(c)["text"] for c in tree["columns"]])
            df.to_excel(path, index=False)
            messagebox.showinfo("Export", f"Report exported to {path}")

    def export_tree_to_pdf(tree):
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                            filetypes=[("PDF files", "*.pdf")])
        if path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            # Header
            for col in tree["columns"]:
                pdf.cell(30, 10, tree.heading(col)["text"], 1, 0, "C")
            pdf.ln()
            pdf.set_font("Arial", "", 10)
            # Rows
            for i in tree.get_children():
                values = tree.item(i)["values"]
                for val in values:
                    pdf.cell(30, 10, str(val), 1, 0, "C")
                pdf.ln()
            pdf.output(path)
            messagebox.showinfo("Export", f"Report exported to {path}")

    btn_export_excel_mem.config(command=lambda: export_tree_to_excel(tree_member))
    btn_export_pdf_mem.config(command=lambda: export_tree_to_pdf(tree_member))
    btn_export_excel_tr.config(command=lambda: export_tree_to_excel(tree_trainer))
    btn_export_pdf_tr.config(command=lambda: export_tree_to_pdf(tree_trainer))
    btn_export_excel_eq.config(command=lambda: export_tree_to_excel(tree_equipment))
    btn_export_pdf_eq.config(command=lambda: export_tree_to_pdf(tree_equipment))
