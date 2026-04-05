import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
try:
    from PIL import Image, ImageTk
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False
    print("Warning: Pillow library not found. Image support will be limited.")
    print("To fix this, run: pip install Pillow")
import shutil
from datetime import datetime

# Constants & Paths
DATA_DIR = "data" 
IMAGE_DIR = "images"
INV_FILE = os.path.join(DATA_DIR, "inventory.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
EXP_FILE = os.path.join(DATA_DIR, "expenses.csv")

# Theme Colors
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "sidebar_bg": "#2c3e50",
        "sidebar_fg": "#ffffff",
        "card_bg": "#ffffff",
        "main_bg": "#ffffff",
        "button_bg": "#34495e",
        "button_fg": "#ffffff",
        "hover_bg": "#46637f",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000"
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "sidebar_bg": "#121212",
        "sidebar_fg": "#ffffff",
        "card_bg": "#2d2d2d",
        "main_bg": "#2d2d2d",
        "button_bg": "#3d3d3d",
        "button_fg": "#ffffff",
        "hover_bg": "#555555",
        "entry_bg": "#3d3d3d",
        "entry_fg": "#ffffff"
    }
}

def hex_to_rgb(hex_str):
    return tuple(int(hex_str.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    return '#{:02x}{:02x}{:02x}'.format(*rgb_tuple)

def interpolate_color(start_hex, end_hex, progress):
    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)
    res_rgb = tuple(int(s + (e - s) * progress) for s, e in zip(start_rgb, end_rgb))
    return rgb_to_hex(res_rgb)

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
        self.current_theme = "light"
        self.root.configure(bg=THEMES[self.current_theme]["bg"])

        # Data initialization
        self.inventory = DataManager.load_csv(INV_FILE)
        self.sales = DataManager.load_csv(SALES_FILE)
        self.expenses = DataManager.load_csv(EXP_FILE)

        self.setup_ui()

    def setup_ui(self):
        theme = THEMES[self.current_theme]
        # Navigation Sidebar
        self.sidebar = tk.Frame(self.root, bg=theme["sidebar_bg"], width=200)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="MAIN MENU", fg=theme["sidebar_fg"], bg=theme["sidebar_bg"], font=("Arial", 12, "bold"), pady=20).pack()

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Inventory", self.show_inventory),
            ("Sales", self.show_sales),
            ("Expenses", self.show_expenses),
        ]

        self.nav_buttons = []
        for text, command in buttons:
            btn = tk.Button(self.sidebar, text=text, command=command, bg=theme["button_bg"], fg=theme["button_fg"], relief="flat", padx=20, pady=10, width=15)
            btn.pack(pady=5)
            self.nav_buttons.append(btn)
            self.bind_hover(btn, theme["button_bg"], theme["hover_bg"])
        
        # Theme Toggle Button
        self.theme_btn = tk.Button(self.sidebar, text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode", 
                                  command=self.toggle_theme, bg="#f1c40f", fg="black", relief="flat", padx=20, pady=10, width=15)
        self.theme_btn.pack(side="bottom", pady=20)
        self.bind_hover(self.theme_btn, "#f1c40f", "#f39c12")

        # Main Content Area
        self.main_frame = tk.Frame(self.root, bg=theme["main_bg"])
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.show_dashboard()

    def bind_hover(self, widget, normal_color, hover_color):
        widget.bind("<Enter>", lambda e: self.animate_color(widget, normal_color, hover_color))
        widget.bind("<Leave>", lambda e: self.animate_color(widget, hover_color, normal_color))

    def animate_color(self, widget, start_hex, end_hex, steps=10, current_step=0):
        if current_step <= steps:
            progress = current_step / steps
            new_color = interpolate_color(start_hex, end_hex, progress)
            try:
                widget.configure(bg=new_color)
                self.root.after(10, lambda: self.animate_color(widget, start_hex, end_hex, steps, current_step + 1))
            except: pass

    def fade_in_frame(self, frame, delay=0):
        frame.place(relx=0.5, rely=0.55, anchor="center") # Start slightly lower
        def slide():
            for i in range(10):
                self.root.after(delay + i*15, lambda i=i: frame.place(relx=0.5, rely=0.55 - (i*0.005), anchor="center"))
        slide()

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        theme = THEMES[self.current_theme]
        
        self.root.configure(bg=theme["bg"])
        self.sidebar.configure(bg=theme["sidebar_bg"])
        self.main_frame.configure(bg=theme["main_bg"])
        
        # Update sidebar labels
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
        
        # Update nav buttons
        for btn in self.nav_buttons:
            btn.configure(bg=theme["button_bg"], fg=theme["button_fg"])
            self.bind_hover(btn, theme["button_bg"], theme["hover_bg"])
            
        # Update theme button
        self.theme_btn.configure(text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode")
        self.bind_hover(self.theme_btn, "#f1c40f", "#f39c12")
        
        # Refresh current view to apply theme
        current_view = getattr(self, "current_view", "dashboard")
        if current_view == "dashboard": self.show_dashboard()
        elif current_view == "inventory": self.show_inventory()
        elif current_view == "sales": self.show_sales()
        elif current_view == "expenses": self.show_expenses()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.current_view = "dashboard"
        self.clear_frame()
        theme = THEMES[self.current_theme]
        self.main_frame.configure(bg=theme["main_bg"])
        
        # Container for animation
        container = tk.Frame(self.main_frame, bg=theme["main_bg"])
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Business Dashboard", font=("Arial", 20, "bold"), bg=theme["main_bg"], fg=theme["fg"]).pack(pady=20)

        stats_frame = tk.Frame(container, bg=theme["main_bg"])
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
            # Staggered entry
            card.grid_remove()
            self.root.after(i*100, lambda c=card: c.grid())

    def show_inventory(self):
        self.current_view = "inventory"
        self.clear_frame()
        theme = THEMES[self.current_theme]
        self.main_frame.configure(bg=theme["main_bg"])

        container = tk.Frame(self.main_frame, bg=theme["main_bg"])
        container.pack(fill="both", expand=True)

        top_frame = tk.Frame(container, bg=theme["main_bg"])
        top_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(top_frame, text="Inventory Manager", font=("Arial", 16, "bold"), bg=theme["main_bg"], fg=theme["fg"]).pack(side="left")
        
        button_frame = tk.Frame(top_frame, bg=theme["main_bg"])
        button_frame.pack(side="right")
        
        tk.Button(button_frame, text="+ Add Product", command=self.add_product_window, bg="#2ecc71", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="- Remove Product", command=self.remove_product, bg="#e74c3c", fg="white").pack(side="left", padx=5)

        columns = ("ID", "Name", "Qty", "Price", "Image")
        
        # Treeview styling for dark mode
        style = ttk.Style()
        if self.current_theme == "dark":
            style.theme_use("clam")
            style.configure("Treeview", background=theme["card_bg"], foreground=theme["fg"], fieldbackground=theme["card_bg"], bordercolor="#444", lightcolor="#444", darkcolor="#444")
            style.configure("Treeview.Heading", background="#333", foreground="white", relief="flat")
            style.map("Treeview", background=[('selected', '#4a90e2')])
        else:
            style.theme_use("default")

        self.tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.preview_product_image)

        self.img_preview_label = tk.Label(container, text="Select a product to see image", bg=theme["main_bg"], fg=theme["fg"])
        self.img_preview_label.pack(pady=10)
        self.refresh_inventory_table()

    def refresh_inventory_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.inventory:
            self.tree.insert("", "end", values=(row['ID'], row['Name'], row['Quantity'], row['Price'], row['Image']))

    def remove_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected product?"):
            item = self.tree.item(selected[0])
            prod_id = str(item['values'][0])
            self.inventory = [p for p in self.inventory if str(p['ID']) != prod_id]
            DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "Image"])
            self.refresh_inventory_table()
            messagebox.showinfo("Success", "Product removed successfully.")

    def preview_product_image(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        img_name = item['values'][4]
        img_path = os.path.join(IMAGE_DIR, img_name)

        theme = THEMES[self.current_theme]
        if PILLOW_INSTALLED and img_name and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                self.img_preview_label.config(image=photo, text="")
                self.img_preview_label.image = photo
            except Exception as e:
                self.img_preview_label.config(image="", text=f"Error: {e}", fg=theme["fg"])
        else:
            self.img_preview_label.config(image="", text="No Image Available", fg=theme["fg"])

    def add_product_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Product")
        win.geometry("300x450")
        theme = THEMES[self.current_theme]
        win.configure(bg=theme["bg"])

        fields = ["Name", "Quantity", "Price"]
        entries = {}
        for f in fields:
            tk.Label(win, text=f, bg=theme["bg"], fg=theme["fg"]).pack()
            e = tk.Entry(win, bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
            e.pack()
            entries[f] = e

        self.selected_img_path = "" 
        def select_img():
            self.selected_img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
            if self.selected_img_path:
                lbl_img.config(text=os.path.basename(self.selected_img_path))

        tk.Button(win, text="Select Image", command=select_img, bg=theme["button_bg"], fg=theme["button_fg"]).pack(pady=10)
        lbl_img = tk.Label(win, text="No image selected", bg=theme["bg"], fg=theme["fg"])
        lbl_img.pack()

        def save():
            try:
                name = entries["Name"].get()
                qty = int(entries["Quantity"].get())
                price = float(entries["Price"].get())

                img_name = "default.png"
                if self.selected_img_path:
                    img_name = os.path.basename(self.selected_img_path)
                    shutil.copy(self.selected_img_path, os.path.join(IMAGE_DIR, img_name))

                new_id = str(len(self.inventory) + 1)
                self.inventory.append({"ID": new_id, "Name": name, "Quantity": qty, "Price": price, "Image": img_name})
                DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "Image"])

                messagebox.showinfo("Success", "Product added!")
                win.destroy()
                self.refresh_inventory_table()
            except ValueError:
                messagebox.showerror("Error", "Invalid Input. Ensure Qty and Price are numeric.")

        tk.Button(win, text="Save Product", bg="#2ecc71", fg="white", command=save).pack(pady=20)

    def show_sales(self):
        self.current_view = "sales"
        self.clear_frame()
        theme = THEMES[self.current_theme]
        self.main_frame.configure(bg=theme["main_bg"])

        container = tk.Frame(self.main_frame, bg=theme["main_bg"])
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Sales Records", font=("Arial", 16, "bold"), bg=theme["main_bg"], fg=theme["fg"]).pack(pady=10)

        sale_form = tk.Frame(container, bg=theme["card_bg"], pady=10)
        sale_form.pack(fill="x", padx=20)

        tk.Label(sale_form, text="Select Product:", bg=theme["card_bg"], fg=theme["fg"]).grid(row=0, column=0)
        prod_names = [p['Name'] for p in self.inventory]
        self.sale_prod_var = tk.StringVar()
        prod_dropdown = ttk.Combobox(sale_form, textvariable=self.sale_prod_var, values=prod_names)
        prod_dropdown.grid(row=0, column=1)

        tk.Label(sale_form, text="Quantity:", bg=theme["card_bg"], fg=theme["fg"]).grid(row=0, column=2)
        self.sale_qty_ent = tk.Entry(sale_form, bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
        self.sale_qty_ent.grid(row=0, column=3)

        tk.Button(sale_form, text="Process Sale", command=self.process_sale, bg="#2ecc71", fg="white").grid(row=0, column=4, padx=10)
        tk.Button(sale_form, text="Remove Sale", command=self.remove_sale, bg="#e74c3c", fg="white").grid(row=0, column=5, padx=10)

        columns = ("ID", "Product", "Qty", "Total", "Date")
        
        style = ttk.Style()
        if self.current_theme == "dark":
            style.theme_use("clam")
            style.configure("Treeview", background=theme["card_bg"], foreground=theme["fg"], fieldbackground=theme["card_bg"], bordercolor="#444", lightcolor="#444", darkcolor="#444")
            style.configure("Treeview.Heading", background="#333", foreground="white", relief="flat")
        else:
            style.theme_use("default")

        self.sales_tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            self.sales_tree.heading(col, text=col)
        self.sales_tree.pack(fill="both", expand=True, padx=20, pady=10)

        for s in self.sales:
            self.sales_tree.insert("", "end", values=(s["ID"], s['Product'], s['Qty'], s['Total'], s['Date']))

    def remove_sale(self):
        selected = self.sales_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a sale record to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected sale record?"):
            item = self.sales_tree.item(selected[0])
            sale_id = str(item['values'][0])
            self.sales = [s for s in self.sales if str(s['ID']) != sale_id]
            DataManager.save_csv(SALES_FILE, self.sales, ["ID", "Product", "Qty", "Total", "Date"])
            self.show_sales()
            messagebox.showinfo("Success", "Sale record removed successfully.")

    def process_sale(self):
        p_name = self.sale_prod_var.get()
        try:
            qty_to_sell = int(self.sale_qty_ent.get())
            product = next((p for p in self.inventory if p['Name'] == p_name), None)

            if product and int(product['Quantity']) >= qty_to_sell:
                product['Quantity'] = int(product['Quantity']) - qty_to_sell
                total_price = qty_to_sell * float(product['Price'])

                new_sale = {
                    "ID": len(self.sales) + 1,
                    "Product": p_name,
                    "Qty": qty_to_sell,
                    "Total": total_price,
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                self.sales.append(new_sale)

                DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "Image"])
                DataManager.save_csv(SALES_FILE, self.sales, ["ID", "Product", "Qty", "Total", "Date"])

                messagebox.showinfo("Success", f"Sold! Total: ₱{total_price:.2f}")
                self.show_sales()
            else:
                messagebox.showerror("Error", "Insufficient stock or invalid product!")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def show_expenses(self):
        self.current_view = "expenses"
        self.clear_frame()
        theme = THEMES[self.current_theme]
        self.main_frame.configure(bg=theme["main_bg"])

        container = tk.Frame(self.main_frame, bg=theme["main_bg"])
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Expense Tracker", font=("Arial", 16, "bold"), bg=theme["main_bg"], fg=theme["fg"]).pack(pady=10)

        exp_form = tk.Frame(container, bg=theme["card_bg"], pady=10)
        exp_form.pack(fill="x", padx=20)

        tk.Label(exp_form, text="Description:", bg=theme["card_bg"], fg=theme["fg"]).grid(row=0, column=0)
        desc_ent = tk.Entry(exp_form, bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
        desc_ent.grid(row=0, column=1)
        
        tk.Label(exp_form, text="Amount:", bg=theme["card_bg"], fg=theme["fg"]).grid(row=0, column=2)
        amt_ent = tk.Entry(exp_form, bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
        amt_ent.grid(row=0, column=3)

        def add_exp():
            try:
                new_exp = {
                    "ID": len(self.expenses) + 1,
                    "Desc": desc_ent.get(),
                    "Amount": float(amt_ent.get()),
                    "Date": datetime.now().strftime("%Y-%m-%d")
                }
                self.expenses.append(new_exp)
                DataManager.save_csv(EXP_FILE, self.expenses, ["ID", "Desc", "Amount", "Date"])
                self.show_expenses()
            except:
                messagebox.showerror("Error", "Invalid amount")
        tk.Button(exp_form, text="Add Expense", command=add_exp, bg="#3498db", fg="white").grid(row=0, column=4, padx=10)
        tk.Button(exp_form, text="Remove Expense", command=self.remove_expense, bg="#e74c3c", fg="white").grid(row=0, column=5, padx=10)

        columns = ("ID", "Desc", "Amount", "Date")
        
        style = ttk.Style()
        if self.current_theme == "dark":
            style.theme_use("clam")
            style.configure("Treeview", background=theme["card_bg"], foreground=theme["fg"], fieldbackground=theme["card_bg"], bordercolor="#444", lightcolor="#444", darkcolor="#444")
            style.configure("Treeview.Heading", background="#333", foreground="white", relief="flat")
        else:
            style.theme_use("default")

        self.expenses_tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            self.expenses_tree.heading(col, text=col)
        self.expenses_tree.pack(fill="both", expand=True, padx=20, pady=10)
        for e in self.expenses:
            self.expenses_tree.insert("", "end", values=(e['ID'], e['Desc'], e['Amount'], e['Date']))

    def remove_expense(self):
        selected = self.expenses_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense record to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected expense record?"):
            item = self.expenses_tree.item(selected[0])
            exp_id = str(item['values'][0])
            self.expenses = [e for e in self.expenses if str(e['ID']) != exp_id]
            DataManager.save_csv(EXP_FILE, self.expenses, ["ID", "Desc", "Amount", "Date"])
            self.show_expenses()
            messagebox.showinfo("Success", "Expense record removed successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
