import tkinter as tk
from tkinter import ttk
from services import get_dashboard_stats

class MainWindow(tk.Frame):
    def __init__(self, parent, user_info, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info
        self.app_controller = app_controller # To handle navigation

        self.create_widgets()
        self.update_stats()

    def create_widgets(self):
        # Main layout frames
        nav_frame = ttk.Frame(self)
        nav_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        stats_frame = ttk.Frame(self)
        stats_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Navigation Buttons ---
        inventory_button = ttk.Button(nav_frame, text="Inventory", command=self.app_controller.show_inventory_view)
        inventory_button.pack(side=tk.LEFT, padx=5)

        sales_button = ttk.Button(nav_frame, text="Sales", command=self.app_controller.show_sales_view)
        sales_button.pack(side=tk.LEFT, padx=5)

        orders_button = ttk.Button(nav_frame, text="Orders", command=self.app_controller.show_order_view)
        orders_button.pack(side=tk.LEFT, padx=5)

        reports_button = ttk.Button(nav_frame, text="Reports")
        reports_button.pack(side=tk.LEFT, padx=5)

        # Add User Management button only for Admins
        if self.user_info['role'] == 'Admin':
            users_button = ttk.Button(nav_frame, text="User Management")
            users_button.pack(side=tk.LEFT, padx=5)

        logout_button = ttk.Button(nav_frame, text="Logout", command=self.logout)
        logout_button.pack(side=tk.RIGHT, padx=5)

        # --- Statistics Frames ---
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        # Total Sales Today
        sales_labelframe = ttk.LabelFrame(stats_frame, text="Total Sales Today")
        sales_labelframe.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.sales_label = ttk.Label(sales_labelframe, text="0.00 LKR", font=("Arial", 24))
        self.sales_label.pack(padx=20, pady=20)

        # Near Expiry Items
        expiry_labelframe = ttk.LabelFrame(stats_frame, text="Items Nearing Expiry (30 days)")
        expiry_labelframe.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.expiry_label = ttk.Label(expiry_labelframe, text="0 Items", font=("Arial", 24))
        self.expiry_label.pack(padx=20, pady=20)

        # Low Stock Alerts
        stock_labelframe = ttk.LabelFrame(stats_frame, text="Low Stock Alerts")
        stock_labelframe.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.stock_label = ttk.Label(stock_labelframe, text="0 Items", font=("Arial", 24))
        self.stock_label.pack(padx=20, pady=20)

    def update_stats(self):
        """Fetches stats from the service layer and updates the UI."""
        try:
            stats = get_dashboard_stats()
            self.sales_label.config(text=f"{stats['total_sales_today']:.2f} LKR")
            self.expiry_label.config(text=f"{stats['near_expiry_items']} Items")
            self.stock_label.config(text=f"{stats['low_stock_items']} Items")
        except Exception as e:
            print(f"Error updating dashboard stats: {e}")
            # Optionally show an error message in the UI
            self.sales_label.config(text="Error")
            self.expiry_label.config(text="Error")
            self.stock_label.config(text="Error")

    def logout(self):
        """Calls the main app controller to handle logout."""
        self.app_controller.show_login_window()
