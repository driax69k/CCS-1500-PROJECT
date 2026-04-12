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
DATA_DIR = "data" 
IMAGE_DIR = "images"
INV_FILE = os.path.join(DATA_DIR, "inventory.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
EXP_FILE = os.path.join(DATA_DIR, "expenses.csv")
CAT_FILE = os.path.join(DATA_DIR, "catalog.csv")

# Ensure directories exist
for folder in [DATA_DIR, IMAGE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

class DataManager:
    @staticmethod
    def load_csv(filepath):
        if not os.path.exists(filepath):
            return []
        with open(filepath, mode='r', newline='') as f:
            return list(csv.DictReader(f))

    @staticmethod
    def save_csv(filepath, data, fieldnames):
        with open(filepath, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Inventory & Accounting System")
        self.root.geometry("1100x650")
        self.root.configure(bg="#f0f0f0")

        self.inventory = DataManager.load_csv(INV_FILE)
        self.sales = DataManager.load_csv(SALES_FILE)
        self.expenses = DataManager.load_csv(EXP_FILE)
        self.catalog = DataManager.load_csv(CAT_FILE)

        self.setup_ui()

    def setup_ui(self):
        self.sidebar = tk.Frame(self.root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="MAIN MENU", fg="white", bg="#2c3e50", font=("Arial", 12, "bold"), pady=20).pack()

        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Master Catalog", self.show_catalog),
            ("Inventory", self.show_inventory),
            ("Sales", self.show_sales),
            ("Expenses", self.show_expenses),
        ]

        for text, command in nav_buttons:
            tk.Button(self.sidebar, text=text, command=command, bg="#34495e", fg="white", relief="flat", padx=20, pady=10, width=15).pack(pady=5)
        
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(side="right", fill="both", expand=True)
        self.show_dashboard()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- DASHBOARD ---
    def show_dashboard(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Business Dashboard", font=("Arial", 20, "bold"), bg="white").pack(pady=20)
        stats_frame = tk.Frame(self.main_frame, bg="white")
        stats_frame.pack(pady=10)

        total_stock_val = sum(float(i['Price']) * int(i['Quantity']) for i in self.inventory)
        total_sales = sum(float(s['Total']) for s in self.sales)
        total_exp = sum(float(e['Amount']) for e in self.expenses)
        net_profit = total_sales - total_exp

        cards = [
            ("Total Products", len(self.inventory), "#3498db"),
            ("Stock Value", f"₱{total_stock_val:.2f}", "#f1c40f"),
            ("Total Sales", f"₱{total_sales:.2f}", "#2ecc71"),
            ("Net Profit", f"₱{net_profit:.2f}", "#e67e22"),
        ]

        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=color, width=200, height=100, padx=20, pady=20)
            card.grid(row=0, column=i, padx=10)
            tk.Label(card, text=title, bg=color, fg="white", font=("Arial", 10)).pack()
            tk.Label(card, text=value, bg=color, fg="white", font=("Arial", 14, "bold")).pack()

    # --- MASTER CATALOG ---
    def show_catalog(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Master Product Catalog", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        
        entry_frame = tk.Frame(self.main_frame, bg="white")
        entry_frame.pack(pady=10)

        tk.Label(entry_frame, text="Product Name:", bg="white").grid(row=0, column=0)
        cat_ent = tk.Entry(entry_frame)
        cat_ent.grid(row=0, column=1, padx=5)

        def add_cat():
            name = cat_ent.get().strip()
            if name and not any(p['Name'].lower() == name.lower() for p in self.catalog):
                self.catalog.append({"Name": name})
                DataManager.save_csv(CAT_FILE, self.catalog, ["Name"])
                self.show_catalog()
            else:
                messagebox.showwarning("Error", "Product name empty or duplicate.")

        tk.Button(entry_frame, text="Add to Catalog", command=add_cat, bg="#3498db", fg="white").grid(row=0, column=2)

        self.cat_tree = ttk.Treeview(self.main_frame, columns=("Name"), show="headings")
        self.cat_tree.heading("Name", text="Product Name")
        self.cat_tree.pack(fill="both", expand=True, padx=50, pady=10)

        for p in self.catalog:
            self.cat_tree.insert("", "end", values=(p['Name'],))

        def remove_cat():
            selected = self.cat_tree.selection()
            if selected:
                name = self.cat_tree.item(selected[0])['values'][0]
                self.catalog = [p for p in self.catalog if p['Name'] != name]
                DataManager.save_csv(CAT_FILE, self.catalog, ["Name"])
                self.show_catalog()

        tk.Button(self.main_frame, text="Remove Selected", command=remove_cat, bg="#e74c3c", fg="white").pack(pady=10)

    # --- INVENTORY ---
    def show_inventory(self):
        self.clear_frame()
        top_frame = tk.Frame(self.main_frame, bg="white")
        top_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(top_frame, text="Inventory Manager", font=("Arial", 16, "bold"), bg="white").pack(side="left")
        
        button_frame = tk.Frame(top_frame, bg="white")
        button_frame.pack(side="right")
        
        tk.Button(button_frame, text="Adjust Stock/Price", command=self.add_product_window, bg="#2ecc71", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Entry", command=self.remove_product, bg="#e74c3c", fg="white").pack(side="left", padx=5)

        columns = ("ID", "Name", "Qty", "Price", "Image")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.preview_product_image)

        self.img_preview_label = tk.Label(self.main_frame, text="Select a product to see image", bg="white")
        self.img_preview_label.pack(pady=10)
        self.refresh_inventory_table()

    def refresh_inventory_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.inventory:
            self.tree.insert("", "end", values=(row['ID'], row['Name'], row['Quantity'], row['Price'], row['Image']))

    def remove_product(self):
        selected = self.tree.selection()
        if not selected: return
        if messagebox.askyesno("Confirm", "Remove this product from active inventory?"):
            item = self.tree.item(selected[0])
            prod_id = str(item['values'][0])
            self.inventory = [p for p in self.inventory if str(p['ID']) != prod_id]
            DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "Image"])
            self.refresh_inventory_table()

    def add_product_window(self):
        if not self.catalog:
            messagebox.showwarning("Catalog Empty", "Add products to Master Catalog first.")
            return

        win = tk.Toplevel(self.root)
        win.title("Adjust Stock & Price")
        win.geometry("350x450")

        tk.Label(win, text="Select Product:", font=("Arial", 10, "bold")).pack(pady=5)
        prod_var = tk.StringVar()
        dropdown = ttk.Combobox(win, textvariable=prod_var, values=[p['Name'] for p in self.catalog], state="readonly")
        dropdown.pack(pady=5)

        tk.Label(win, text="Qty Change (use '-' to subtract):").pack(pady=5)
        qty_ent = tk.Entry(win)
        qty_ent.insert(0, "0")
        qty_ent.pack()

        tk.Label(win, text="New Unit Price:").pack(pady=5)
        price_ent = tk.Entry(win)
        price_ent.pack()

        self.selected_img_path = ""
        def select_img():
            self.selected_img_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
            if self.selected_img_path:
                lbl_img.config(text=f"Selected: {os.path.basename(self.selected_img_path)}")

        tk.Button(win, text="Change Image", command=select_img).pack(pady=10)
        lbl_img = tk.Label(win, text="No new image selected", font=("Arial", 8), fg="gray")
        lbl_img.pack()

        def on_prod_select(event):
            existing = next((p for p in self.inventory if p['Name'] == prod_var.get()), None)
            if existing:
                price_ent.delete(0, tk.END)
                price_ent.insert(0, existing['Price'])
        dropdown.bind("<<ComboboxSelected>>", on_prod_select)

        def save_adjustment():
            try:
                name = prod_var.get()
                qty_change = int(qty_ent.get())
                new_price = float(price_ent.get())
                if not name: return

                existing = next((p for p in self.inventory if p['Name'] == name), None)
                
                img_name = "default.png"
                if self.selected_img_path:
                    img_name = os.path.basename(self.selected_img_path)
                    shutil.copy(self.selected_img_path, os.path.join(IMAGE_DIR, img_name))
                elif existing:
                    img_name = existing['Image']

                if existing:
                    new_qty = int(existing['Quantity']) + qty_change
                    if new_qty < 0:
                        messagebox.showerror("Error", "Resulting stock cannot be negative.")
                        return
                    existing['Quantity'] = str(new_qty)
                    existing['Price'] = f"{new_price:.2f}"
                    existing['Image'] = img_name
                else:
                    if qty_change < 0:
                        messagebox.showerror("Error", "Cannot start new stock with negative quantity.")
                        return
                    new_id = str(len(self.inventory) + 1)
                    self.inventory.append({
                        "ID": new_id, "Name": name, "Quantity": str(qty_change), 
                        "Price": f"{new_price:.2f}", "Image": img_name
                    })

                DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "Image"])
                self.refresh_inventory_table()
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers.")

        tk.Button(win, text="Apply Changes", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=save_adjustment).pack(pady=20)

    def preview_product_image(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        img_name = item['values'][4]
        img_path = os.path.join(IMAGE_DIR, img_name)
        if PILLOW_INSTALLED and img_name and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((120, 120))
                photo = ImageTk.PhotoImage(img)
                self.img_preview_label.config(image=photo, text="")
                self.img_preview_label.image = photo
            except: self.img_preview_label.config(image="", text="Image Error")
        else: self.img_preview_label.config(image="", text="No Image")

    # --- SALES ---
    def show_sales(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Sales Records", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        sale_form = tk.Frame(self.main_frame, bg="#ecf0f1", pady=10)
        sale_form.pack(fill="x", padx=20)

        tk.Label(sale_form, text="Product:").grid(row=0, column=0)
        inv_names = [p['Name'] for p in self.inventory]
        self.sale_prod_var = tk.StringVar()
        prod_dropdown = ttk.Combobox(sale_form, textvariable=self.sale_prod_var, values=inv_names, state="readonly")
        prod_dropdown.grid(row=0, column=1, padx=5)

        tk.Label(sale_form, text="Qty:").grid(row=0, column=2)
        self.sale_qty_ent = tk.Entry(sale_form)
        self.sale_qty_ent.grid(row=0, column=3, padx=5)

        tk.Button(sale_form, text="Process Sale", command=self.process_sale, bg="#2ecc71", fg="white").grid(row=0, column=4, padx=5)
        tk.Button(sale_form, text="Clear All Sales", command=self.clear_sales_history, bg="#e74c3c", fg="white").grid(row=0, column=5, padx=5)

        columns = ("ID", "Product", "Qty", "Total", "Date")
        self.sales_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns: self.sales_tree.heading(col, text=col)
        self.sales_tree.pack(fill="both", expand=True, padx=20, pady=10)
        for s in self.sales: self.sales_tree.insert("", "end", values=(s["ID"], s['Product'], s['Qty'], s['Total'], s['Date']))

    def process_sale(self):
        p_name = self.sale_prod_var.get()
        try:
            qty_to_sell = int(self.sale_qty_ent.get())
            product = next((p for p in self.inventory if p['Name'] == p_name), None)
            if product and int(product['Quantity']) >= qty_to_sell:
                product['Quantity'] = str(int(product['Quantity']) - qty_to_sell)
                total_price = qty_to_sell * float(product['Price'])
                new_id = len(self.sales) + 1
                new_sale = {"ID": new_id, "Product": p_name, "Qty": qty_to_sell, "Total": f"{total_price:.2f}", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                self.sales.append(new_sale)
                DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "Image"])
                DataManager.save_csv(SALES_FILE, self.sales, ["ID", "Product", "Qty", "Total", "Date"])
                self.show_sales()
            else: messagebox.showerror("Error", "Check stock")
        except: messagebox.showerror("Error", "Invalid entry")

    def clear_sales_history(self):
        if self.sales and messagebox.askyesno("Confirm", "Delete ALL sales?"):
            self.sales = []
            DataManager.save_csv(SALES_FILE, self.sales, ["ID", "Product", "Qty", "Total", "Date"])
            self.show_sales()

    # --- EXPENSES ---
    def show_expenses(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Expense Tracker", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        exp_form = tk.Frame(self.main_frame, bg="#ecf0f1", pady=10)
        exp_form.pack(fill="x", padx=20)
        tk.Label(exp_form, text="Desc:").grid(row=0, column=0)
        desc_ent = tk.Entry(exp_form)
        desc_ent.grid(row=0, column=1)
        tk.Label(exp_form, text="Amount:").grid(row=0, column=2)
        amt_ent = tk.Entry(exp_form)
        amt_ent.grid(row=0, column=3, padx=5)

        def add_exp():
            try:
                new_id = len(self.expenses) + 1
                new_exp = {"ID": new_id, "Desc": desc_ent.get(), "Amount": f"{float(amt_ent.get()):.2f}", "Date": datetime.now().strftime("%Y-%m-%d")}
                self.expenses.append(new_exp)
                DataManager.save_csv(EXP_FILE, self.expenses, ["ID", "Desc", "Amount", "Date"])
                self.show_expenses()
            except: messagebox.showerror("Error", "Invalid amount")
        
        tk.Button(exp_form, text="Add Expense", command=add_exp, bg="#3498db", fg="white").grid(row=0, column=4, padx=5)
        tk.Button(exp_form, text="Clear All Expenses", command=self.clear_expenses_history, bg="#e74c3c", fg="white").grid(row=0, column=5, padx=5)

        columns = ("ID", "Desc", "Amount", "Date")
        self.expenses_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns: self.expenses_tree.heading(col, text=col)
        self.expenses_tree.pack(fill="both", expand=True, padx=20, pady=10)
        for e in self.expenses: self.expenses_tree.insert("", "end", values=(e['ID'], e['Desc'], e['Amount'], e['Date']))

    def clear_expenses_history(self):
        if self.expenses and messagebox.askyesno("Confirm", "Delete ALL expenses?"):
            self.expenses = []
            DataManager.save_csv(EXP_FILE, self.expenses, ["ID", "Desc", "Amount", "Date"])
            self.show_expenses()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()