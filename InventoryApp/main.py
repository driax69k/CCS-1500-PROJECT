import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
try:
    from PIL import Image, ImageTk
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False
import shutil
from datetime import datetime

# Constants & Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data") 
IMAGE_DIR = os.path.join(BASE_DIR, "images")
INV_FILE = os.path.join(DATA_DIR, "inventory.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
CAT_FILE = os.path.join(DATA_DIR, "catalog.csv")

class Colors:
    BG_MAIN = "#f8fafc"
    BG_SIDEBAR = "#1e293b"
    BG_CARD = "#ffffff"
    BORDER = "#e2e8f0"
    PRIMARY = "#3b82f6"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    TEXT_PRIMARY = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    NAV_HOVER = "#334155"
    NAV_ACTIVE = "#3b82f6"

# Fieldnames
CAT_FIELDS = ["Name", "Description"]
INV_FIELDS = ["ID", "Name", "Quantity", "UnitPrice", "SellingPrice", "Image"]
SALES_FIELDS = ["ID", "Product", "Qty", "UnitPrice", "SellingPrice", "Total", "Profit", "Date"]

# Ensure directories exist
for folder in [DATA_DIR, IMAGE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

class DataManager:
    @staticmethod
    def load_csv(filepath, fieldnames):
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return []
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except Exception:
            return []

    @staticmethod
    def save_csv(filepath, data, fieldnames):
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ADDMR.CO Inventory")
        self.root.geometry("1200x750")
        self.root.configure(bg=Colors.BG_MAIN)

        self.inventory = DataManager.load_csv(INV_FILE, INV_FIELDS)
        self.sales = DataManager.load_csv(SALES_FILE, SALES_FIELDS)
        self.catalog = DataManager.load_csv(CAT_FILE, CAT_FIELDS)
        
        self.normalize_data()
        
        self.nav_btns = {}
        self.current_view = "Dashboard"

        self.setup_styles()
        self.setup_ui()

    def normalize_data(self):
        # Normalize Inventory
        for item in self.inventory:
            if 'Price' in item and ('SellingPrice' not in item or not item['SellingPrice']):
                item['SellingPrice'] = item['Price']
            
            # Ensure all fields exist
            for field in INV_FIELDS:
                if field not in item:
                    item[field] = "0" if field in ["Quantity", "UnitPrice", "SellingPrice"] else ""
        
        # Normalize Sales
        for sale in self.sales:
            for field in SALES_FIELDS:
                if field not in sale:
                    sale[field] = "0" if field in ["Qty", "UnitPrice", "SellingPrice", "Total", "Profit"] else ""

    def add_placeholder(self, ent, text):
        ent.delete(0, tk.END)
        ent.insert(0, text)
        ent.config(fg=Colors.TEXT_SECONDARY)
        
        def on_focus_in(e):
            if ent.get() == text:
                ent.delete(0, tk.END)
                ent.config(fg=Colors.TEXT_PRIMARY)
        
        def on_focus_out(e):
            if not ent.get():
                ent.insert(0, text)
                ent.config(fg=Colors.TEXT_SECONDARY)
        
        ent.bind("<FocusIn>", on_focus_in)
        ent.bind("<FocusOut>", on_focus_out)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam") # 'clam' allows more customization than 'vista/xpnative'
        
        # Treeview styling
        style.configure("Treeview", 
                        background=Colors.BG_CARD, 
                        foreground=Colors.TEXT_PRIMARY, 
                        fieldbackground=Colors.BG_CARD,
                        rowheight=35,
                        font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", Colors.PRIMARY)])
        
        style.configure("Treeview.Heading", 
                        background=Colors.BG_MAIN, 
                        foreground=Colors.TEXT_SECONDARY, 
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        
        # Custom Entry styling (simulated)
        style.configure("TEntry", padding=5)

    def setup_ui(self):
        # Sidebar Styling
        self.sidebar = tk.Frame(self.root, bg=Colors.BG_SIDEBAR, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo/Brand
        brand_frame = tk.Frame(self.sidebar, bg=Colors.BG_SIDEBAR, pady=40)
        brand_frame.pack(fill="x")
        tk.Label(brand_frame, text="ADDMR.CO", fg="white", bg=Colors.BG_SIDEBAR, 
                 font=("Segoe UI", 18, "bold")).pack()
        tk.Label(brand_frame, text="INVENTORY SYSTEM", fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SIDEBAR, 
                 font=("Segoe UI", 8, "bold")).pack()

        nav_items = [
            ("Dashboard", "📊", self.show_dashboard),
            ("Master Catalog", "📋", self.show_catalog),
            ("Inventory", "📦", self.show_inventory),
            ("Sales", "🛒", self.show_sales),
            ("Summary Report", "📈", self.show_summary),
        ]

        for text, icon, command in nav_items:
            self.create_nav_btn(text, icon, command)
        
        self.main_frame = tk.Frame(self.root, bg=Colors.BG_MAIN)
        self.main_frame.pack(side="right", fill="both", expand=True)
        self.show_dashboard()

    def create_nav_btn(self, text, icon, command):
        btn_frame = tk.Frame(self.sidebar, bg=Colors.BG_SIDEBAR, padx=10, pady=2)
        btn_frame.pack(fill="x")
        
        def on_click():
            self.current_view = text
            self.update_nav_styles()
            command()

        btn = tk.Button(btn_frame, text=f"  {icon}  {text}", command=on_click, 
                        bg=Colors.BG_SIDEBAR, fg="white", relief="flat", 
                        anchor="w", font=("Segoe UI", 10),
                        activebackground=Colors.NAV_HOVER, activeforeground="white", 
                        cursor="hand2", bd=0)
        btn.pack(fill="x", ipady=10)
        
        btn.bind("<Enter>", lambda e: self.on_nav_hover(btn, True))
        btn.bind("<Leave>", lambda e: self.on_nav_hover(btn, False))
        
        self.nav_btns[text] = btn

    def on_nav_hover(self, btn, is_hover):
        if self.current_view not in self.nav_btns or self.nav_btns[self.current_view] != btn:
            btn.configure(bg=Colors.NAV_HOVER if is_hover else Colors.BG_SIDEBAR)

    def update_nav_styles(self):
        for text, btn in self.nav_btns.items():
            if text == self.current_view:
                btn.configure(bg=Colors.NAV_ACTIVE, fg="white")
            else:
                btn.configure(bg=Colors.BG_SIDEBAR, fg="white")

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- DASHBOARD ---
    def show_dashboard(self):
        self.inventory = DataManager.load_csv(INV_FILE, INV_FIELDS)
        self.sales = DataManager.load_csv(SALES_FILE, SALES_FIELDS)
        self.clear_frame()
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40, pady=30)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Business Dashboard", font=("Segoe UI", 24, "bold"), 
                 bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY).pack(side="left")
        
        tk.Label(header_frame, text=datetime.now().strftime("%A, %B %d, %Y"), 
                 font=("Segoe UI", 10), bg=Colors.BG_MAIN, fg=Colors.TEXT_SECONDARY).pack(side="right", pady=10)

        # Content area with padding
        content_scroll = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40)
        content_scroll.pack(fill="both", expand=True)

        stats_frame = tk.Frame(content_scroll, bg=Colors.BG_MAIN)
        stats_frame.pack(fill="x")

        # Calculations
        today = datetime.now().strftime("%Y-%m-%d")
        
        total_stock_cost = sum(float(i.get('UnitPrice', 0)) * int(i.get('Quantity', 0)) for i in self.inventory)
        total_stock_val = sum(float(i.get('SellingPrice', 0)) * int(i.get('Quantity', 0)) for i in self.inventory)
        
        total_sales_all = sum(float(s.get('Total', 0)) for s in self.sales)
        total_profit_all = sum(float(s.get('Profit', 0)) for s in self.sales)
        
        daily_sales = sum(float(s.get('Total', 0)) for s in self.sales if s.get('Date', '').startswith(today))
        daily_profit = sum(float(s.get('Profit', 0)) for s in self.sales if s.get('Date', '').startswith(today))

        cards = [
            ("Inventory Cost", f"₱{total_stock_cost:,.2f}", Colors.PRIMARY, "📦"),
            ("Inventory Value", f"₱{total_stock_val:,.2f}", Colors.WARNING, "💰"),
            ("Today's Sales", f"₱{daily_sales:,.2f}", Colors.SUCCESS, "🛒"),
            ("Today's Profit", f"₱{daily_profit:,.2f}", Colors.DANGER, "💸"),
            ("Lifetime Revenue", f"₱{total_sales_all:,.2f}", "#06b6d4", "🛍️"),
            ("Lifetime Profit", f"₱{total_profit_all:,.2f}", "#8b5cf6", "📈"),
        ]

        for i, (title, value, color, icon) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=Colors.BG_CARD, highlightthickness=1, highlightbackground=Colors.BORDER)
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            
            # Icon and Title
            top_row = tk.Frame(card, bg=Colors.BG_CARD, padx=20, pady=15)
            top_row.pack(fill="x")
            
            tk.Label(top_row, text=icon, font=("Segoe UI", 20), bg=Colors.BG_CARD).pack(side="left")
            tk.Label(top_row, text=title.upper(), font=("Segoe UI", 9, "bold"), 
                     bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=10)
            
            # Value
            val_label = tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), 
                                 bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY, padx=20)
            val_label.pack(anchor="w", pady=(0, 20))
            
            # Bottom stripe
            tk.Frame(card, bg=color, height=4).pack(side="bottom", fill="x")

        # Configure grid weights
        for j in range(3):
            stats_frame.grid_columnconfigure(j, weight=1)

    # --- MASTER CATALOG ---
    def show_catalog(self):
        self.catalog = DataManager.load_csv(CAT_FILE, CAT_FIELDS)
        self.clear_frame()
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40, pady=30)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Product Catalog", font=("Segoe UI", 24, "bold"), 
                 bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY).pack(side="left")

        # Main Content
        content_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40)
        content_frame.pack(fill="both", expand=True)

        # Quick Add Form
        entry_card = tk.Frame(content_frame, bg=Colors.BG_CARD, padx=20, pady=20, 
                             highlightthickness=1, highlightbackground=Colors.BORDER)
        entry_card.pack(fill="x", pady=(0, 20))

        tk.Label(entry_card, text="Add New Product to Catalog", font=("Segoe UI", 10, "bold"), 
                 bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        tk.Label(entry_card, text="Product Name", bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")
        cat_name_ent = tk.Entry(entry_card, font=("Segoe UI", 10), width=30, highlightthickness=1, highlightbackground=Colors.BORDER, bd=0)
        cat_name_ent.grid(row=2, column=0, padx=(0, 20), pady=(5, 15), sticky="w")

        tk.Label(entry_card, text="Description", bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w")
        cat_desc_ent = tk.Entry(entry_card, font=("Segoe UI", 10), width=50, highlightthickness=1, highlightbackground=Colors.BORDER, bd=0)
        cat_desc_ent.grid(row=2, column=1, padx=(0, 20), pady=(5, 15), sticky="w")

        def add_cat():
            name = cat_name_ent.get().strip()
            desc = cat_desc_ent.get().strip()
            # Allow duplicate names only if the description is different
            if name and not any(p['Name'].lower() == name.lower() and p.get('Description', '').lower() == desc.lower() for p in self.catalog):
                self.catalog.append({"Name": name, "Description": desc})
                DataManager.save_csv(CAT_FILE, self.catalog, CAT_FIELDS)
                self.show_catalog()
            else:
                messagebox.showwarning("Error", "Product with this name and description already exists or name is empty.")

        tk.Button(entry_card, text="+ Add Product", command=add_cat, bg=Colors.PRIMARY, fg="white", 
                  relief="flat", font=("Segoe UI", 10, "bold"), padx=25, pady=8, cursor="hand2").grid(row=2, column=2, sticky="e")

        # Search Card
        search_card = tk.Frame(content_frame, bg=Colors.BG_CARD, padx=20, pady=15, 
                              highlightthickness=1, highlightbackground=Colors.BORDER)
        search_card.pack(fill="x", pady=(0, 20))
        
        tk.Label(search_card, text="🔍", font=("Segoe UI", 14), bg=Colors.BG_CARD).pack(side="left")
        
        self.cat_search_var = tk.StringVar()
        self.cat_search_ent = tk.Entry(search_card, textvariable=self.cat_search_var, font=("Segoe UI", 11), 
                                      highlightthickness=0, bd=0, bg=Colors.BG_CARD)
        self.cat_search_ent.pack(side="left", fill="x", expand=True, padx=15)
        
        self.cat_placeholder = "Search by name or description..."
        self.add_placeholder(self.cat_search_ent, self.cat_placeholder)

        self.cat_count_lbl = tk.Label(search_card, text="Found 0 items", font=("Segoe UI", 9, "bold"), 
                                      bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.cat_count_lbl.pack(side="right")
        
        self.cat_search_var.trace_add("write", lambda *args: self.filter_catalog())

        # Table
        table_container = tk.Frame(content_frame, bg=Colors.BG_CARD, highlightthickness=1, highlightbackground=Colors.BORDER)
        table_container.pack(fill="both", expand=True, pady=(0, 20))
        
        self.cat_tree = ttk.Treeview(table_container, columns=("Name", "Description"), show="headings")
        self.cat_tree.heading("Name", text="PRODUCT NAME")
        self.cat_tree.heading("Description", text="DESCRIPTION")
        self.cat_tree.column("Name", width=300)
        self.cat_tree.column("Description", width=450)
        self.cat_tree.pack(fill="both", expand=True)
        
        self.filter_catalog()

    def filter_catalog(self):
        query = self.cat_search_var.get().lower()
        if query == self.cat_placeholder.lower(): query = ""
        
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
            
        count = 0
        for p in self.catalog:
            name = p.get('Name','').lower()
            desc = p.get('Description','').lower()
            if not query or query in name or query in desc:
                self.cat_tree.insert("", "end", values=(p.get('Name',''), p.get('Description','')))
                count += 1
        
        self.cat_count_lbl.config(text=f"Found {count} items")

    # --- INVENTORY ---
    def show_inventory(self):
        self.inventory = DataManager.load_csv(INV_FILE, INV_FIELDS)
        self.catalog = DataManager.load_csv(CAT_FILE, CAT_FIELDS)
        self.clear_frame()
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40, pady=30)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Inventory Manager", font=("Segoe UI", 24, "bold"), 
                 bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY).pack(side="left")
        
        tk.Button(header_frame, text="+ Adjust Stock/Price", command=self.add_product_window, 
                  bg=Colors.SUCCESS, fg="white", relief="flat", font=("Segoe UI", 10, "bold"), 
                  padx=20, pady=10, cursor="hand2").pack(side="right")

        # Main Content
        content_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40)
        content_frame.pack(fill="both", expand=True)

        # Search & Summary Card
        search_card = tk.Frame(content_frame, bg=Colors.BG_CARD, padx=20, pady=15, 
                              highlightthickness=1, highlightbackground=Colors.BORDER)
        search_card.pack(fill="x", pady=(0, 20))
        
        # Search part
        search_left = tk.Frame(search_card, bg=Colors.BG_CARD)
        search_left.pack(side="left", fill="x", expand=True)
        
        tk.Label(search_left, text="🔍", font=("Segoe UI", 14), bg=Colors.BG_CARD).pack(side="left")
        
        self.inv_search_var = tk.StringVar()
        self.inv_search_ent = tk.Entry(search_left, textvariable=self.inv_search_var, font=("Segoe UI", 11), 
                                      highlightthickness=0, bd=0, bg=Colors.BG_CARD)
        self.inv_search_ent.pack(side="left", fill="x", expand=True, padx=15)
        
        self.inv_placeholder = "Search by name or ID..."
        self.add_placeholder(self.inv_search_ent, self.inv_placeholder)
        self.inv_search_var.trace_add("write", lambda *args: self.refresh_inventory_table())

        # Summary part
        self.inv_summary_lbl = tk.Label(search_card, text="Total Units: 0 | Low Stock: 0", 
                                        font=("Segoe UI", 9, "bold"), bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.inv_summary_lbl.pack(side="right", padx=(20, 0))

        # Container for table and preview
        paned_content = tk.Frame(content_frame, bg=Colors.BG_MAIN)
        paned_content.pack(fill="both", expand=True, pady=(0, 20))

        # Left side: Table
        table_card = tk.Frame(paned_content, bg=Colors.BG_CARD, highlightthickness=1, highlightbackground=Colors.BORDER)
        table_card.pack(side="left", fill="both", expand=True)

        columns = ("ID", "Name", "Qty", "UnitPrice", "SellingPrice", "TotalUnit", "TotalSelling")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        
        column_configs = {
            "ID": (50, "ID"),
            "Name": (200, "PRODUCT NAME"),
            "Qty": (80, "QTY"),
            "UnitPrice": (110, "UNIT COST"),
            "SellingPrice": (110, "SELLING PRICE"),
            "TotalUnit": (130, "STOCK VALUE (COST)"),
            "TotalSelling": (130, "STOCK VALUE (SALE)")
        }

        for col, (width, anchor) in column_configs.items():
            self.tree.heading(col, text=anchor)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.preview_product_image)

        # Right side: Image Preview
        preview_card = tk.Frame(paned_content, bg=Colors.BG_CARD, width=320, 
                               highlightthickness=1, highlightbackground=Colors.BORDER)
        preview_card.pack(side="right", fill="y", padx=(20, 0))
        preview_card.pack_propagate(False)

        header_preview = tk.Frame(preview_card, bg=Colors.BG_MAIN, pady=10)
        header_preview.pack(fill="x")
        tk.Label(header_preview, text="PRODUCT IMAGE", font=("Segoe UI", 9, "bold"), 
                 bg=Colors.BG_MAIN, fg=Colors.TEXT_SECONDARY).pack()
        
        self.img_preview_label = tk.Label(preview_card, text="Select a product\nto view image", 
                                          bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, font=("Segoe UI", 10))
        self.img_preview_label.pack(pady=40, fill="both", expand=True)

        self.refresh_inventory_table()

    def refresh_inventory_table(self):
        query = getattr(self, 'inv_search_var', None)
        query = query.get().lower() if query else ""
        if query == self.inv_placeholder.lower(): query = ""
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_units = 0
        low_stock_count = 0
        
        for row in self.inventory:
            name = row.get('Name', '')
            p_id = row.get('ID', '')
            if query and (query not in name.lower() and query not in p_id.lower()):
                continue
                
            qty = int(row.get('Quantity', 0))
            u_price = float(row.get('UnitPrice', 0))
            s_price = float(row.get('SellingPrice', 0))
            
            total_u = qty * u_price
            total_s = qty * s_price
            
            total_units += qty
            if qty < 10: low_stock_count += 1
            
            # Stock status tagging
            if qty < 10:
                tag = "low_stock"
            elif qty < 25:
                tag = "med_stock"
            else:
                tag = "high_stock"
            
            # Zebra striping overlay
            zebra = "even" if len(self.tree.get_children()) % 2 == 0 else "odd"
            
            self.tree.insert("", "end", values=(
                p_id, name, qty, 
                f"₱{u_price:,.2f}", f"₱{s_price:,.2f}", 
                f"₱{total_u:,.2f}", f"₱{total_s:,.2f}",
                row.get('Image', 'default.png')
            ), tags=(tag, zebra))
        
        # Configure tags for visual feedback
        self.tree.tag_configure("low_stock", foreground=Colors.DANGER)
        self.tree.tag_configure("med_stock", foreground=Colors.WARNING)
        
        self.tree.tag_configure("odd", background="#ffffff")
        self.tree.tag_configure("even", background="#f8fafc")
        
        if hasattr(self, 'inv_summary_lbl'):
            self.inv_summary_lbl.config(text=f"Total Units: {total_units} | Low Stock: {low_stock_count}")

    def preview_product_image(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        img_name = item['values'][7] if len(item['values']) > 7 else "default.png"
        img_path = os.path.join(IMAGE_DIR, img_name)
        if PILLOW_INSTALLED and img_name and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((250, 250))
                photo = ImageTk.PhotoImage(img)
                self.img_preview_label.config(image=photo, text="")
                self.img_preview_label.image = photo
            except: self.img_preview_label.config(image="", text="Image Error")
        else: self.img_preview_label.config(image="", text="No Image Found")

    # --- SALES ---
    def show_sales(self):
        self.sales = DataManager.load_csv(SALES_FILE, SALES_FIELDS)
        self.inventory = DataManager.load_csv(INV_FILE, INV_FIELDS)
        self.normalize_data()
        self.clear_frame()
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40, pady=30)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Sales Transactions", font=("Segoe UI", 24, "bold"), 
                 bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY).pack(side="left")

        # Main Content
        content_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40)
        content_frame.pack(fill="both", expand=True)

        # Sale Form Card
        form_card = tk.Frame(content_frame, bg=Colors.BG_CARD, padx=25, pady=25, 
                            highlightthickness=1, highlightbackground=Colors.BORDER)
        form_card.pack(fill="x", pady=(0, 20))

        tk.Label(form_card, text="New Sale Transaction", font=("Segoe UI", 10, "bold"), 
                 bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))

        tk.Label(form_card, text="Select Product", bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")
        # Use only p['Name'] because the description is already included in the Name field of the inventory
        inv_names = [p['Name'] for p in self.inventory if int(p.get('Quantity', 0)) > 0]
        self.sale_prod_var = tk.StringVar()
        prod_dropdown = ttk.Combobox(form_card, textvariable=self.sale_prod_var, values=inv_names, state="readonly", font=("Segoe UI", 10), width=40)
        prod_dropdown.grid(row=2, column=0, padx=(0, 20), pady=(5, 0), sticky="w")

        tk.Label(form_card, text="Quantity", bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w")
        self.sale_qty_ent = tk.Entry(form_card, font=("Segoe UI", 10), width=15, highlightthickness=1, highlightbackground=Colors.BORDER, bd=0)
        self.sale_qty_ent.grid(row=2, column=1, padx=(0, 20), pady=(5, 0), sticky="w", ipady=3)

        tk.Button(form_card, text="Confirm Sale", command=self.process_sale, bg=Colors.SUCCESS, fg="white", 
                  relief="flat", font=("Segoe UI", 10, "bold"), padx=30, pady=8, cursor="hand2").grid(row=2, column=2, sticky="e")

        # Search Bar for Sales
        search_frame = tk.Frame(content_frame, bg=Colors.BG_MAIN)
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="🔍", font=("Segoe UI", 12), bg=Colors.BG_MAIN).pack(side="left")
        self.sales_search_var = tk.StringVar()
        sales_search_ent = tk.Entry(search_frame, textvariable=self.sales_search_var, font=("Segoe UI", 10), 
                                   highlightthickness=1, highlightbackground=Colors.BORDER, bd=0)
        sales_search_ent.pack(side="left", fill="x", expand=True, padx=10, ipady=5)
        
        self.sales_placeholder = "Search by product name..."
        self.add_placeholder(sales_search_ent, self.sales_placeholder)
        self.sales_search_var.trace_add("write", lambda *args: self.refresh_sales_table())

        # Table
        table_container = tk.Frame(content_frame, bg=Colors.BG_CARD, highlightthickness=1, highlightbackground=Colors.BORDER)
        table_container.pack(fill="both", expand=True, pady=(0, 20))
        
        columns = ("ID", "Product", "Qty", "UnitPrice", "SellingPrice", "Total", "Profit", "Date")
        self.sales_tree = ttk.Treeview(table_container, columns=columns, show="headings")
        
        col_configs = {
            "ID": (50, "ID"), 
            "Product": (200, "PRODUCT"), 
            "Qty": (70, "QTY"), 
            "UnitPrice": (100, "COST"), 
            "SellingPrice": (100, "PRICE"), 
            "Total": (110, "TOTAL"), 
            "Profit": (110, "PROFIT"), 
            "Date": (150, "DATE")
        }
        for col, (width, title) in col_configs.items():
            self.sales_tree.heading(col, text=title)
            self.sales_tree.column(col, width=width, anchor="center")

        self.sales_tree.pack(fill="both", expand=True)
        self.refresh_sales_table()

    def refresh_sales_table(self):
        query = getattr(self, 'sales_search_var', None)
        query = query.get().lower() if query else ""
        if query == self.sales_placeholder.lower(): query = ""
        
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
            
        for s in reversed(self.sales): # Show latest first
            product = s.get('Product', '')
            if query and query not in product.lower():
                continue
                
            tag = "even" if len(self.sales_tree.get_children()) % 2 == 0 else "odd"
            self.sales_tree.insert("", "end", values=(
                s.get("ID"), product, s.get('Qty'), 
                f"₱{float(s.get('UnitPrice', 0)):,.2f}", f"₱{float(s.get('SellingPrice', 0)):,.2f}", 
                f"₱{float(s.get('Total', 0)):,.2f}", f"₱{float(s.get('Profit', 0)):,.2f}", s.get('Date')
            ), tags=(tag,))
            
        self.sales_tree.tag_configure("odd", background="#ffffff")
        self.sales_tree.tag_configure("even", background="#f8fafc")

    def process_sale(self):
        p_name = self.sale_prod_var.get()
        if not p_name:
            messagebox.showwarning("Warning", "Please select a product.")
            return

        try:
            qty_text = self.sale_qty_ent.get()
            if not qty_text:
                messagebox.showwarning("Warning", "Please enter a quantity.")
                return
                
            qty_to_sell = int(qty_text)
            if qty_to_sell <= 0:
                messagebox.showerror("Error", "Quantity must be greater than zero.")
                return
            
            # Find the product in current inventory
            product = next((p for p in self.inventory if p['Name'] == p_name), None)
            
            if not product:
                messagebox.showerror("Error", f"Product '{p_name}' not found in inventory.")
                return

            available_qty = int(product.get('Quantity', 0))
            if available_qty >= qty_to_sell:
                u_price = float(product.get('UnitPrice', 0))
                s_price = float(product.get('SellingPrice', 0))
                
                # Update inventory
                new_qty = available_qty - qty_to_sell
                if new_qty <= 0:
                    self.inventory.remove(product)
                else:
                    product['Quantity'] = str(new_qty)
                
                # Create new record
                total_sale = qty_to_sell * s_price
                total_cost = qty_to_sell * u_price
                profit = total_sale - total_cost
                
                # Generate new ID safely
                max_id = 0
                for s in self.sales:
                    try:
                        max_id = max(max_id, int(s.get('ID', 0)))
                    except ValueError: continue
                
                new_id = max_id + 1
                new_sale = {
                    "ID": str(new_id), 
                    "Product": p_name, 
                    "Qty": str(qty_to_sell), 
                    "UnitPrice": f"{u_price:.2f}",
                    "SellingPrice": f"{s_price:.2f}",
                    "Total": f"{total_sale:.2f}", 
                    "Profit": f"{profit:.2f}",
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                self.sales.append(new_sale)
                
                DataManager.save_csv(INV_FILE, self.inventory, INV_FIELDS)
                DataManager.save_csv(SALES_FILE, self.sales, SALES_FIELDS)
                
                messagebox.showinfo("Success", f"Sale processed!\nTotal: ₱{total_sale:,.2f}\nProfit: ₱{profit:,.2f}")
                self.show_sales()
            else:
                messagebox.showerror("Error", f"Insufficient stock!\nAvailable: {available_qty}\nRequested: {qty_to_sell}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid whole number for quantity.")
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {str(e)}")

    # --- SUMMARY REPORT (DAILY) ---
    def show_summary(self):
        self.clear_frame()
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40, pady=30)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Daily Summary Report", font=("Segoe UI", 24, "bold"), 
                 bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY).pack(side="left")

        # Main Content
        content_frame = tk.Frame(self.main_frame, bg=Colors.BG_MAIN, padx=40)
        content_frame.pack(fill="both", expand=True)

        today = datetime.now().strftime("%Y-%m-%d")
        daily_sales_list = [s for s in self.sales if s.get('Date', '').startswith(today)]
        
        t_qty = sum(int(s.get('Qty', 0)) for s in daily_sales_list)
        t_revenue = sum(float(s.get('Total', 0)) for s in daily_sales_list)
        t_profit = sum(float(s.get('Profit', 0)) for s in daily_sales_list)
        
        # Stats Cards for Summary
        stats_box = tk.Frame(content_frame, bg=Colors.BG_MAIN)
        stats_box.pack(fill="x", pady=(0, 20))
        
        summary_cards = [
            ("Items Sold", str(t_qty), Colors.PRIMARY),
            ("Total Revenue", f"₱{t_revenue:,.2f}", Colors.SUCCESS),
            ("Net Profit", f"₱{t_profit:,.2f}", Colors.WARNING),
        ]
        
        for i, (title, val, color) in enumerate(summary_cards):
            card = tk.Frame(stats_box, bg=Colors.BG_CARD, padx=20, pady=15, 
                            highlightthickness=1, highlightbackground=Colors.BORDER)
            card.grid(row=0, column=i, padx=(0, 20 if i < 2 else 0), sticky="nsew")
            tk.Label(card, text=title.upper(), font=("Segoe UI", 9, "bold"), bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
            tk.Label(card, text=val, font=("Segoe UI", 16, "bold"), bg=Colors.BG_CARD, fg=color).pack(anchor="w", pady=(5, 0))
            stats_box.grid_columnconfigure(i, weight=1)

        # Table Container
        table_card = tk.Frame(content_frame, bg=Colors.BG_CARD, padx=20, pady=20, 
                             highlightthickness=1, highlightbackground=Colors.BORDER)
        table_card.pack(fill="both", expand=True, pady=(0, 20))
        
        tk.Label(table_card, text="Today's Product Summary", font=("Segoe UI", 11, "bold"), 
                 bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, 15))
        
        sum_tree = ttk.Treeview(table_card, columns=("Product", "Qty", "Total", "Profit"), show="headings", height=10)
        sum_tree.heading("Product", text="PRODUCT")
        sum_tree.heading("Qty", text="TOTAL QTY")
        sum_tree.heading("Total", text="TOTAL REVENUE")
        sum_tree.heading("Profit", text="TOTAL PROFIT")
        
        for col in ("Product", "Qty", "Total", "Profit"):
            sum_tree.column(col, anchor="center")
        
        sum_tree.pack(fill="both", expand=True)
        
        # Aggregate by product
        summary_data = {}
        for s in daily_sales_list:
            prod = s.get('Product')
            qty = int(s.get('Qty', 0))
            total = float(s.get('Total', 0))
            profit = float(s.get('Profit', 0))
            
            if prod not in summary_data:
                summary_data[prod] = {'Qty': 0, 'Total': 0.0, 'Profit': 0.0}
            
            summary_data[prod]['Qty'] += qty
            summary_data[prod]['Total'] += total
            summary_data[prod]['Profit'] += profit

        for prod, data in summary_data.items():
            sum_tree.insert("", "end", values=(prod, data['Qty'], f"₱{data['Total']:,.2f}", f"₱{data['Profit']:,.2f}"))

        def export_summary():
            messagebox.showinfo("Export", "Daily Report exported to 'daily_report.txt'")
            with open("daily_report.txt", "w", encoding="utf-8") as f:
                f.write(f"DAILY SUMMARY REPORT - {today}\n")
                f.write("="*30 + "\n")
                f.write(f"Total Items Sold: {t_qty}\n")
                f.write(f"Total Revenue: ₱{t_revenue:.2f}\n")
                f.write(f"Total Profit: ₱{t_profit:.2f}\n")
                f.write("\nProduct Summary:\n")
                for prod, data in summary_data.items():
                    f.write(f"{prod} | Total Qty: {data['Qty']} | Total Revenue: ₱{data['Total']:.2f} | Total Profit: ₱{data['Profit']:.2f}\n")

        tk.Button(content_frame, text="Download Daily Report (.txt)", command=export_summary, bg=Colors.PRIMARY, fg="white", 
                  relief="flat", font=("Segoe UI", 10, "bold"), padx=25, pady=10, cursor="hand2").pack(pady=(0, 30))

    def add_product_window(self):
        if not self.catalog:
            messagebox.showwarning("Catalog Empty", "Add products to Master Catalog first.")
            return

        win = tk.Toplevel(self.root)
        win.title("Adjust Stock & Price")
        win.geometry("450x650")
        win.configure(bg=Colors.BG_CARD)
        win.transient(self.root)
        win.grab_set()

        main_win_frame = tk.Frame(win, bg=Colors.BG_CARD, padx=30, pady=30)
        main_win_frame.pack(fill="both", expand=True)

        tk.Label(main_win_frame, text="ADJUST STOCK & PRICE", font=("Segoe UI", 14, "bold"), 
                 bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY).pack(pady=(0, 25))

        def create_field(label, var=None, is_combo=False, combo_vals=None):
            tk.Label(main_win_frame, text=label, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            if is_combo:
                ent = ttk.Combobox(main_win_frame, textvariable=var, values=combo_vals, state="readonly", font=("Segoe UI", 10))
            else:
                ent = tk.Entry(main_win_frame, font=("Segoe UI", 10), highlightthickness=1, highlightbackground=Colors.BORDER, bd=0)
            ent.pack(fill="x", pady=(5, 20), ipady=5 if not is_combo else 0)
            return ent

        prod_var = tk.StringVar()
        dropdown = create_field("Select Product", var=prod_var, is_combo=True, 
                                combo_vals=[f"{p['Name']} ({p.get('Description', 'No Desc')})" for p in self.catalog])
        qty_ent = create_field("Quantity Adjustment (+ / -)")
        qty_ent.insert(0, "0")
        u_price_ent = create_field("Unit Cost (Supplier Price)")
        s_price_ent = create_field("Selling Price (Market Price)")

        self.selected_img_path = ""
        def select_img():
            self.selected_img_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
            if self.selected_img_path:
                lbl_img.config(text=f"Selected: {os.path.basename(self.selected_img_path)}", fg=Colors.SUCCESS)

        tk.Button(main_win_frame, text="📁 Choose Product Image", command=select_img, bg="#f1f5f9", fg=Colors.TEXT_PRIMARY, 
                  relief="flat", font=("Segoe UI", 9), pady=8).pack(fill="x", pady=(0, 5))
        lbl_img = tk.Label(main_win_frame, text="No new image selected", font=("Segoe UI", 8), bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY)
        lbl_img.pack(pady=(0, 20))

        def on_prod_select(event):
            selected_combined = prod_var.get()
            existing = next((p for p in self.inventory if p['Name'] == selected_combined), None)
            if existing:
                u_price_ent.delete(0, tk.END)
                u_price_ent.insert(0, existing.get('UnitPrice', '0.00'))
                s_price_ent.delete(0, tk.END)
                s_price_ent.insert(0, existing.get('SellingPrice', existing.get('Price', '0.00')))
        
        dropdown.bind("<<ComboboxSelected>>", on_prod_select)

        def save_adjustment():
            try:
                name = prod_var.get() # This is now "Name (Description)"
                qty_change = int(qty_ent.get())
                u_price = float(u_price_ent.get())
                s_price = float(s_price_ent.get())
                if not name: return

                existing = next((p for p in self.inventory if p['Name'] == name), None)
                
                img_name = "default.png"
                if self.selected_img_path:
                    ext = os.path.splitext(self.selected_img_path)[1]
                    # Use sanitized combined name for filename
                    safe_name = name.replace(' ', '_').replace('(', '').replace(')', '')
                    img_name = f"{safe_name}_{int(datetime.now().timestamp())}{ext}"
                    shutil.copy(self.selected_img_path, os.path.join(IMAGE_DIR, img_name))
                elif existing:
                    img_name = existing.get('Image', 'default.png')

                if existing:
                    new_qty = int(existing.get('Quantity', 0)) + qty_change
                    if new_qty < 0:
                        messagebox.showerror("Error", "Resulting stock cannot be negative.")
                        return
                    if new_qty == 0:
                        self.inventory.remove(existing)
                    else:
                        existing['Quantity'] = str(new_qty)
                        existing['UnitPrice'] = f"{u_price:.2f}"
                        existing['SellingPrice'] = f"{s_price:.2f}"
                        existing['Image'] = img_name
                    if 'Price' in existing: del existing['Price']
                else:
                    if qty_change < 0:
                        messagebox.showerror("Error", "Cannot start new stock with negative quantity.")
                        return
                    if qty_change == 0:
                        messagebox.showwarning("Warning", "Cannot add a new product with zero stock.")
                        return
                    
                    max_id = max([int(p.get('ID', 0)) for p in self.inventory], default=0)
                    new_id = str(max_id + 1)
                    self.inventory.append({
                        "ID": new_id, "Name": name, "Quantity": str(qty_change), 
                        "UnitPrice": f"{u_price:.2f}", "SellingPrice": f"{s_price:.2f}", 
                        "Image": img_name
                    })

                DataManager.save_csv(INV_FILE, self.inventory, INV_FIELDS)
                self.refresh_inventory_table()
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers.")

        tk.Button(main_win_frame, text="Save Changes", bg=Colors.PRIMARY, fg="white", 
                  relief="flat", font=("Segoe UI", 10, "bold"), command=save_adjustment, pady=12).pack(fill="x", pady=(10, 0))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
