# Integrated Inventory & Accounting System

A Python-based desktop application designed to streamline business operations by managing inventory, tracking sales, and monitoring expenses in one unified interface.

## 🚀 Features

### 1. Business Dashboard
- **Real-time Statistics**: View total products, current stock value, total sales, and net profit at a glance.
- **Visual Overview**: High-level summary cards for quick financial assessment.

### 2. Inventory Management
- **Add Products**: Easily add new items with name, quantity, price, and product images.
- **Image Support**: Preview product images directly within the application.
- **Remove Products**: Delete outdated or discontinued items from the inventory.
- **Persistence**: All data is automatically saved to `inventory.csv`.

### 3. Sales Tracking
- **Process Sales**: Record transactions by selecting products from the inventory.
- **Automatic Stock Updates**: Selling an item automatically deducts the quantity from the inventory.
- **Sales History**: Keep a detailed log of all transactions, including date, quantity, and total price.
- **Remove Sales**: Delete incorrect or cancelled sales records.

### 4. Expense Tracker
- **Log Expenses**: Track business costs with descriptions and amounts.
- **Financial Monitoring**: Expenses are factored into the net profit calculation on the dashboard.
- **Remove Expenses**: Delete or correct expense entries as needed.

## 🛠️ Prerequisites

To run this application, you need:

1.  **Python 3.x**: Ensure Python is installed on your system.
2.  **Pillow Library**: Required for image processing and previews.
    ```bash
    pip install Pillow
    ```
3.  **Tkinter**: Usually comes pre-installed with Python on Windows. If you are on Linux, you might need:
    ```bash
    sudo apt-get install python3-tk
    ```

## 📂 Project Structure

- `main.py`: The primary application script.
- `data/`: Directory containing CSV files (`inventory.csv`, `sales.csv`, `expenses.csv`) for data storage.
- `images/`: Directory where uploaded product images are stored.

## 📖 How It Works

1.  **Launch**: Run `python InventoryApp/main.py`.
2.  **Navigation**: Use the sidebar to switch between the Dashboard, Inventory, Sales, and Expenses sections.
3.  **Adding Data**:
    - Go to **Inventory** to add your products first.
    - Go to **Sales** to record a sale (ensure you have stock in the inventory).
    - Go to **Expenses** to log any business costs.
4.  **Data Management**:
    - Use the **Remove** buttons in each section to manage your records.
    - Confirm deletions via the pop-up dialogs to prevent accidental data loss.
5.  **Automatic Saving**: The app uses CSV files in the `data/` folder as a lightweight database. Every time you add or remove an item, the files are updated instantly.

---
*Developed for CCS 1500 Project*
