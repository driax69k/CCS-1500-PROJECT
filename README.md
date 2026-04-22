# ADDMR.CO Inventory

A modernized Python-based desktop application for business operations, featuring advanced inventory tracking, sales analytics, and daily financial reporting.

## 🚀 April 20 Key Updates

### 1. Enhanced Business Dashboard
- **Real-time Stats**: View Stock Cost, Stock Value, Daily Sales, Daily Profit, and Total Net Profit.
- **Improved UI**: Modern card-based layout with interactive feedback and better visual hierarchy.

### 2. Comprehensive Inventory Manager
- **Dual Pricing**: Track both **Unit Cost** (Supplier Price) and **Selling Price** (Market Price).
- **Valuation Columns**: Automatic calculation of Total Unit Cost and Total Selling Value for all stock.
- **Image Integration**: Improved product image preview and management.

### 3. Advanced Sales Tracking
- **Profit Analytics**: Every sale now calculates net profit based on the margin between Unit Cost and Selling Price.
- **Detailed Logs**: Records include unit prices at the time of sale for accurate historical reporting.

### 4. Daily Summary Report (Replaces Expenses)
- **Daily Performance**: Instant view of today's total items sold, revenue, and net profit.
- **Transaction History**: List of all today's transactions with timestamps.
- **Export Feature**: Generate a `daily_report.txt` file for record-keeping.

### 5. Master Product Catalog
- **Product Descriptions**: Catalog now supports detailed descriptions for every product.

## 🛠️ Prerequisites

To run this application, you need:

1.  **Python 3.x**: Ensure Python is installed on your system.
2.  **Pillow Library**: Required for image processing and previews.
    ```bash
    pip install Pillow
    ```
3.  **Tkinter**: Usually comes pre-installed with Python on Windows.

## 📂 Project Structure

- `InventoryApp/main.py`: The primary application script.
- `data/`: Directory containing CSV files (`inventory.csv`, `sales.csv`, `catalog.csv`).
- `images/`: Directory for product images.

## 📝 Quick Data Setup

To quickly populate your product list, you can paste the following data directly into `InventoryApp/data/catalog.csv` using a text editor before running the app:

```csv
Name,Description
Mountain Dew,1L
Mountain Dew,1.5L
Coca Cola,1.5L
Sprite,1.5L
```

**Steps:**
1. Open `catalog.csv` in Notepad or VS Code.
2. Ensure the first line is `Name,Description`.
3. Paste the items above and press **Ctrl + S** to save the file.
4. Launch the app and go to the **Master Catalog** tab to see your products.

## 📖 How It Works

1.  **Launch**: Run `python InventoryApp/main.py`. (Tip: Maximize the window for the most immersive experience!)
2.  **Setup**: Start by adding products and their descriptions in the **Master Catalog**.
3.  **Inventory**: Use the **Adjust Stock/Price** button to set your stock levels, unit costs, and selling prices.
4.  **Sales**: Process transactions in the **Sales** tab. Stock and profit are updated automatically.
5.  **Reporting**: Visit the **Summary Report** tab to see your daily business performance and export data.

---
*Developed for CCS 1500 Project*
