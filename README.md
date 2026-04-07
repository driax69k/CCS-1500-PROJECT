# Integrated Inventory & Sales Tracking System

A Python-based desktop application designed to streamline business operations by managing inventory and tracking sales with batch management and daily tracking features.

## Key Features
- **Dashboard**: Real-time summary of total products, stock value, and total sales.
- **Inventory Management**:
    - **Add Products**: Include details like Name, Quantity, Price, Expiry Date, and Remarks.
    - **Batch Management**: Automatically creates a new batch if the expiration date is different for the same product.
    - **Restock Feature**: Easily add quantity to existing inventory entries.
    - **Product Images**: Select and preview product images.
    - **Delete Product**: Remove products and their records from the system.
- **Sales Tracking**:
    - **Record Sales**: Simplified sale processing that automatically deducts stock from the oldest batch first (FIFO).
    - **Daily Summaries**: View daily sales totals and historical tracking directly in the sales view.
    - **Remove Records**: Manage and delete incorrect sale entries.
- **Modern UI**: Theme-based interface with animations, hover effects, and a responsive layout.

## Project Structure
- `InventoryApp/main.py`: The core application file containing logic and GUI.
- `data/`: Directory containing CSV files (`inventory.csv`, `sales.csv`) for data storage.
- `images/`: Directory for product images.

## Usage
1.  **Launch the App**: Run `python InventoryApp/main.py`.
2.  **Navigation**: Use the sidebar to switch between the Dashboard, Inventory, and Sales sections.
3.  **Manage Inventory**:
    - Click **+ Add Product** to register new items or batches.
    - Use **Restock** to update quantities for existing batches.
4.  **Sales**:
    - Go to **Sales** and click **+ Record Sale** to process transactions.
    - Monitor **Daily Sales Summary** for business performance updates.
