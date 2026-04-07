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

# Theme Colors
THEME = {
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
        self.root.title("Integrated Inventory & Sales Tracking System")
        self.root.geometry("1100x650")
        self.root.configure(bg=THEME["bg"])

        # Data initialization
        self.inventory = DataManager.load_csv(INV_FILE)
        self.sales = DataManager.load_csv(SALES_FILE)

        self.setup_ui()

    def setup_ui(self):
        theme = THEME
        # Navigation Sidebar
        self.sidebar = tk.Frame(self.root, bg=theme["sidebar_bg"], width=200)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="MAIN MENU", fg=theme["sidebar_fg"], bg=theme["sidebar_bg"], font=("Arial", 12, "bold"), pady=20).pack()

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Inventory", self.show_inventory),
            ("Sales", self.show_sales),
        ]

        self.nav_buttons = []
        for text, command in buttons:
            btn = tk.Button(self.sidebar, text=text, command=command, bg=theme["button_bg"], fg=theme["button_fg"], relief="flat", padx=20, pady=10, width=15)
            btn.pack(pady=5)
            self.nav_buttons.append(btn)
            self.bind_hover(btn, theme["button_bg"], theme["hover_bg"])
        
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

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.current_view = "dashboard"
        self.clear_frame()
        theme = THEME
        self.main_frame.configure(bg=theme["main_bg"])
        
        # Container for animation
        container = tk.Frame(self.main_frame, bg=theme["main_bg"])
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Business Dashboard", font=("Arial", 20, "bold"), bg=theme["main_bg"], fg=theme["fg"]).pack(pady=20)

        stats_frame = tk.Frame(container, bg=theme["main_bg"])
        stats_frame.pack(pady=10)

        total_stock_val = sum(float(i.get('Price', 0)) * int(i.get('Quantity', 0)) for i in self.inventory)
        total_sales = sum(float(s.get('Total', 0)) for s in self.sales)

        cards = [
            ("Total Products", len(self.inventory), "#3498db"),
            ("Stock Value", f"₱{total_stock_val:.2f}", "#f1c40f"),
            ("Total Sales", f"₱{total_sales:.2f}", "#2ecc71"),
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
        theme = THEME
        self.main_frame.configure(bg=theme["main_bg"])

        container = tk.Frame(self.main_frame, bg=theme["main_bg"])
        container.pack(fill="both", expand=True)

        top_frame = tk.Frame(container, bg=theme["main_bg"])
        top_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(top_frame, text="Inventory Manager", font=("Arial", 16, "bold"), bg=theme["main_bg"], fg=theme["fg"]).pack(side="left")
        
        button_frame = tk.Frame(top_frame, bg=theme["main_bg"])
        button_frame.pack(side="right")
        
        tk.Button(button_frame, text="+ Add Product", command=self.add_product_window, bg="#2ecc71", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="↻ Restock", command=self.restock_product_window, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="- Remove Product", command=self.remove_product, bg="#e74c3c", fg="white").pack(side="left", padx=5)

        columns = ("ID", "Name", "Qty", "Price", "Expiry", "Remarks", "Image")
        
        # Treeview styling
        style = ttk.Style()
        style.theme_use("default")

        self.tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            width = 150 if col in ["Name", "Remarks"] else 80
            self.tree.column(col, width=width)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.preview_product_image)

        self.img_preview_label = tk.Label(container, text="Select a product to see image", bg=theme["main_bg"], fg=theme["fg"])
        self.img_preview_label.pack(pady=10)
        self.refresh_inventory_table()

    def refresh_inventory_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.inventory:
            self.tree.insert("", "end", values=(
                row.get('ID', ''), 
                row.get('Name', ''), 
                row.get('Quantity', ''), 
                row.get('Price', ''), 
                row.get('ExpiryDate', 'N/A'), 
                row.get('Remarks', ''), 
                row.get('Image', 'default.png')
            ))

    def remove_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected product?"):
            item = self.tree.item(selected[0])
            prod_id = str(item['values'][0])
            self.inventory = [p for p in self.inventory if str(p['ID']) != prod_id]
            DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "ExpiryDate", "Remarks", "Image"])
            self.refresh_inventory_table()
            messagebox.showinfo("Success", "Product removed successfully.")

    def preview_product_image(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        img_name = item['values'][6] # Image is now at index 6
        img_path = os.path.join(IMAGE_DIR, img_name)

        theme = THEME
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
        win.geometry("350x550")
        theme = THEME
        win.configure(bg=theme["bg"])

        fields = ["Name", "Quantity", "Price", "Expiry Date (YYYY-MM-DD)", "Remarks"]
        entries = {}
        for f in fields:
            tk.Label(win, text=f, bg=theme["bg"], fg=theme["fg"]).pack()
            e = tk.Entry(win, bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
            e.pack(pady=2)
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
                expiry = entries["Expiry Date (YYYY-MM-DD)"].get()
                remarks = entries["Remarks"].get()

                if not name:
                    messagebox.showerror("Error", "Name is required")
                    return

                img_name = "default.png"
                if self.selected_img_path:
                    img_name = os.path.basename(self.selected_img_path)
                    shutil.copy(self.selected_img_path, os.path.join(IMAGE_DIR, img_name))

                # Check for existing product with same name AND expiry
                existing = next((p for p in self.inventory if p['Name'] == name and p.get('ExpiryDate', '') == expiry), None)
                
                if existing:
                    existing['Quantity'] = int(existing['Quantity']) + qty
                    existing['Price'] = price # Update price if it changed
                    existing['Remarks'] = remarks
                else:
                    new_id = str(max([int(p['ID']) for p in self.inventory] + [0]) + 1)
                    self.inventory.append({
                        "ID": new_id, 
                        "Name": name, 
                        "Quantity": qty, 
                        "Price": price, 
                        "ExpiryDate": expiry,
                        "Remarks": remarks,
                        "Image": img_name
                    })
                
                DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "ExpiryDate", "Remarks", "Image"])

                messagebox.showinfo("Success", "Product added/updated!")
                win.destroy()
                self.refresh_inventory_table()
            except ValueError:
                messagebox.showerror("Error", "Invalid Input. Ensure Qty and Price are numeric.")

        tk.Button(win, text="Save Product", bg="#2ecc71", fg="white", command=save).pack(pady=20)

    def restock_product_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to restock.")
            return
        
        item = self.tree.item(selected[0])
        prod_id = str(item['values'][0])
        product = next((p for p in self.inventory if str(p['ID']) == prod_id), None)
        
        if not product: return

        win = tk.Toplevel(self.root)
        win.title(f"Restock: {product['Name']}")
        win.geometry("300x200")
        theme = THEME
        win.configure(bg=theme["bg"])

        tk.Label(win, text=f"Product: {product['Name']}", bg=theme["bg"], font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(win, text="Add Quantity:", bg=theme["bg"]).pack()
        qty_ent = tk.Entry(win)
        qty_ent.pack(pady=5)

        def save_restock():
            try:
                add_qty = int(qty_ent.get())
                product['Quantity'] = int(product['Quantity']) + add_qty
                DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "ExpiryDate", "Remarks", "Image"])
                messagebox.showinfo("Success", f"Restocked {add_qty} units.")
                win.destroy()
                self.refresh_inventory_table()
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity.")

        tk.Button(win, text="Confirm Restock", bg="#3498db", fg="white", command=save_restock).pack(pady=10)

    def show_sales(self):
        self.current_view = "sales"
        self.clear_frame()
        theme = THEME
        self.main_frame.configure(bg=theme["main_bg"])

        container = tk.Frame(self.main_frame, bg=theme["main_bg"])
        container.pack(fill="both", expand=True)

        top_frame = tk.Frame(container, bg=theme["main_bg"])
        top_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(top_frame, text="Sales & Daily Tracking", font=("Arial", 16, "bold"), bg=theme["main_bg"], fg=theme["fg"]).pack(side="left")
        
        button_frame = tk.Frame(top_frame, bg=theme["main_bg"])
        button_frame.pack(side="right")
        
        tk.Button(button_frame, text="+ Record Sale", command=self.record_sale_window, bg="#2ecc71", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="- Remove Record", command=self.remove_sale, bg="#e74c3c", fg="white").pack(side="left", padx=5)

        # Daily Tracking Section
        tracking_frame = tk.LabelFrame(container, text="Daily Sales Summary", bg=theme["main_bg"], fg=theme["fg"], font=("Arial", 10, "bold"))
        tracking_frame.pack(fill="x", padx=20, pady=10)

        daily_summary = {}
        for s in self.sales:
            date = s['Date'].split(' ')[0]
            daily_summary[date] = daily_summary.get(date, 0) + float(s['Total'])

        # Display last 5 days
        sorted_dates = sorted(daily_summary.keys(), reverse=True)[:5]
        if not sorted_dates:
            tk.Label(tracking_frame, text="No sales recorded yet.", bg=theme["main_bg"], fg=theme["fg"]).pack()
        else:
            for date in sorted_dates:
                summary_line = tk.Frame(tracking_frame, bg=theme["main_bg"])
                summary_line.pack(fill="x", padx=10)
                tk.Label(summary_line, text=date, bg=theme["main_bg"], fg=theme["fg"], width=15, anchor="w").pack(side="left")
                tk.Label(summary_line, text=f"₱{daily_summary[date]:.2f}", bg=theme["main_bg"], fg="#2ecc71", font=("Arial", 10, "bold")).pack(side="right")

        columns = ("ID", "Product", "Qty", "Total", "Date")
        style = ttk.Style()
        style.theme_use("default")

        self.sales_tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100)
        self.sales_tree.pack(fill="both", expand=True, padx=20, pady=10)

        for s in self.sales:
            self.sales_tree.insert("", "end", values=(s.get("ID", ""), s.get('Product', ''), s.get('Qty', ''), s.get('Total', ''), s.get('Date', '')))

    def record_sale_window(self):
        win = tk.Toplevel(self.root)
        win.title("Record New Sale")
        win.geometry("300x250")
        theme = THEME
        win.configure(bg=theme["bg"])

        tk.Label(win, text="Select Product:", bg=theme["bg"]).pack(pady=5)
        # Unique product names
        prod_names = sorted(list(set([p['Name'] for p in self.inventory])))
        prod_var = tk.StringVar()
        prod_dropdown = ttk.Combobox(win, textvariable=prod_var, values=prod_names)
        prod_dropdown.pack(pady=5)

        tk.Label(win, text="Quantity:", bg=theme["bg"]).pack(pady=5)
        qty_ent = tk.Entry(win)
        qty_ent.pack(pady=5)

        def process():
            p_name = prod_var.get()
            try:
                qty_to_sell = int(qty_ent.get())
                if qty_to_sell <= 0: raise ValueError
                
                # Find all batches for this product, sorted by ExpiryDate (FIFO)
                batches = [p for p in self.inventory if p['Name'] == p_name]
                batches.sort(key=lambda x: x.get('ExpiryDate', '9999-99-99')) # N/A goes to end

                total_available = sum(int(b['Quantity']) for b in batches)

                if total_available >= qty_to_sell:
                    remaining_to_sell = qty_to_sell
                    total_price = 0
                    
                    for batch in batches:
                        if remaining_to_sell <= 0: break
                        
                        batch_qty = int(batch['Quantity'])
                        sell_from_batch = min(batch_qty, remaining_to_sell)
                        
                        batch['Quantity'] = batch_qty - sell_from_batch
                        total_price += sell_from_batch * float(batch['Price'])
                        remaining_to_sell -= sell_from_batch

                    new_sale = {
                        "ID": str(max([int(s['ID']) for s in self.sales] + [0]) + 1),
                        "Product": p_name,
                        "Qty": qty_to_sell,
                        "Total": total_price,
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    self.sales.append(new_sale)

                    DataManager.save_csv(INV_FILE, self.inventory, ["ID", "Name", "Quantity", "Price", "ExpiryDate", "Remarks", "Image"])
                    DataManager.save_csv(SALES_FILE, self.sales, ["ID", "Product", "Qty", "Total", "Date"])

                    messagebox.showinfo("Success", f"Sale Recorded! Total: ₱{total_price:.2f}")
                    win.destroy()
                    self.show_sales()
                else:
                    messagebox.showerror("Error", f"Insufficient stock! Available: {total_available}")
            except Exception as e:
                messagebox.showerror("Error", "Invalid input or processing error.")

        tk.Button(win, text="Confirm Sale", bg="#2ecc71", fg="white", command=process).pack(pady=20)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
