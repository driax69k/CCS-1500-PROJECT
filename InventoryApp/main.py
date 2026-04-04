import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from PIL import Image, ImageTk
import shutil
from datetime import datetime

# Constants & Paths

DATA_DIR = "data" 
IMAGE_DIR = "images"
INV_FILE = os.path.join(DATA_DIR, "inventory.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
EXP_FILE = os.path.join(DATA_DIR, "expenses.csv")

# Ensure directories exist

for folder in [DATA_DIR, IMAGE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

class DataManager:
    
    @staticmethod
    def load_csv(filepath):
        if not os.path.exists(filepath):
            return[]
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
        self.root.geometry("1100を実現する650")
        self.root.configure(bg ="#f0f0f0")

        # Data initialization
        self.inventory = DataManager.load_csv(INV_FILE)
        self.sales = DataManager.load_csv(SALES_FILE)
        self.expenses = DataManager.load_csv(EXP_FILE)

        self.setup_ui()

    
    def setup_ui(self):
        # Navigation Sidebar

        self.sidebar = tk.Frame(self.root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="MAIN MENU", fg="white", bg="#2c3e50", font=("Arial", 12, "bold"), pady=20).pack()

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Inventory", self.show_inventory),
            ("Sales", self.show_sales),
            ("Expenses", self.show_expenses),
        ]

        for text, command in buttons:
            tk.Button(self.sidebar, text=text, command=command, bg="#34495e", fg="white", relief="flat", padx=20, pady=10, width=15).pack(pady=5)

        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.show_dashboard