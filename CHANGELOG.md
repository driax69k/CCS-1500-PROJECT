# Changelog

## [1.2.0] - 2026-04-07
### Added
- **Batch Management**: Implemented expiration date tracking. Products with the same name but different expiration dates are now handled as separate batches.
- **FIFO Sales Logic**: Sales now automatically deduct stock from the oldest batches first based on their expiration date.
- **Restock Feature**: Added a new button in the inventory manager to quickly add stock to existing items.
- **Inventory Remarks**: Added a "Remarks" column to the inventory for additional product notes.
- **Daily Sales Tracking**: Added a dedicated summary section in the Sales view to track daily totals.
- **Record Sale Dialog**: Replaced the POS form with a dedicated "Record Sale" window for a cleaner interface.

### Removed
- **Expenses Tracker**: Completely removed the expenses section and related code to focus on inventory and sales.
- **expenses.csv**: Deleted the unused data file.

### Fixed
- **Price Management**: Adding an existing product name with the same expiry now updates the quantity and price of that batch instead of creating a duplicate entry.

---

## [1.1.0] - 2026-04-06
### Added
- **UI Animations & Smooth Transitions**: Hover transitions and staggered dashboard entry effects.
- **Data Removal Functionality**: Added feature to delete products, sales, and expenses.
- **ID-Based Deletion**: Precise record targeting for data integrity.
- **CSV Synchronization**: Real-time mirroring of UI changes to CSV files.
- **Documentation**: Comprehensive README.md created.

### Removed
- **Theme Customization**: Removed the theme toggle engine in favor of a fixed light theme for maintenance.

### Fixed
- **Bug Fix**: Fixed `expenses_tree` global access issue.

---

## [1.0.0] - Prior Release
### Added
- **Initial Release**: Basic inventory, sales, and expenses tracking system.
- **Dashboard Statistics**: Visual cards for total products, stock value, total sales, and net profit.
- **Inventory Management**: CSV-based storage for product details and images.
- **Sales System**: Basic POS-style form to record sales.
- **Expenses Tracker**: Log business costs and calculate net profit.
