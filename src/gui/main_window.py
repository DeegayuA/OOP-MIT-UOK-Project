import tkinter as tk
from tkinter import ttk, messagebox
from services import get_dashboard_stats, get_near_expiry_items, get_low_stock_items
from .widgets.tooltip_button import TooltipButton
from .detailed_alert_view import DetailedAlertView
from .user_management_view import UserManagementView

class MainWindow(tk.Frame):
    def __init__(self, parent, user_info, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info
        self.app_controller = app_controller # To handle navigation

        self.create_widgets()
        self.update_stats()

    def show_near_expiry_details(self, event=None):
        items = get_near_expiry_items()
        if not items:
            messagebox.showinfo("No Items", "There are no items nearing expiry.")
            return

        columns = {
            'name': 'Product Name',
            'batch_number': 'Batch Number',
            'quantity': 'Quantity',
            'expiry_date': 'Expiry Date'
        }
        DetailedAlertView(self, "Items Nearing Expiry", items, columns)

    def show_low_stock_details(self, event=None):
        items = get_low_stock_items()
        if not items:
            messagebox.showinfo("No Items", "There are no items with low stock.")
            return

        columns = {
            'name': 'Product Name',
            'total_stock': 'Current Stock',
            'reorder_level': 'Reorder Level'
        }
        DetailedAlertView(self, "Low Stock Items", items, columns)

    def create_widgets(self):
        # Main layout frames
        nav_frame = ttk.Frame(self)
        nav_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        stats_frame = ttk.Frame(self)
        stats_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Navigation Buttons ---
        inventory_button = TooltipButton(nav_frame, text="Inventory (Ctrl+I)", command=self.app_controller.show_inventory_view, tooltip_text="Open Inventory View (Ctrl+I)")
        inventory_button.pack(side=tk.LEFT, padx=5)

        sales_button = TooltipButton(nav_frame, text="Sales (Ctrl+S)", command=self.app_controller.show_sales_view, tooltip_text="Open Sales View (Ctrl+S)")
        sales_button.pack(side=tk.LEFT, padx=5)

        orders_button = TooltipButton(nav_frame, text="Orders (Ctrl+O)", command=self.app_controller.show_order_view, tooltip_text="Open Order View (Ctrl+O)")
        orders_button.pack(side=tk.LEFT, padx=5)

        if self.user_info['role'] == 'Viewer':
            sales_button.configure(state=tk.DISABLED)
            orders_button.configure(state=tk.DISABLED)

        reports_button = TooltipButton(nav_frame, text="Reports (Ctrl+R)", command=self.app_controller.show_reports_view, tooltip_text="Open Reports View (Ctrl+R)")
        reports_button.pack(side=tk.LEFT, padx=5)

        # Add User Management button only for Admins
        if self.user_info['role'] == 'Admin':
            users_button = TooltipButton(nav_frame, text="User Management", command=self.show_user_management_view, tooltip_text="Manage users")
            users_button.pack(side=tk.LEFT, padx=5)

        help_button = TooltipButton(nav_frame, text="Help (Ctrl+H)", command=self.app_controller.show_help_window, tooltip_text="Show Help (Ctrl+H)")
        help_button.pack(side=tk.LEFT, padx=5)

        logout_button = TooltipButton(nav_frame, text="Logout (Ctrl+L)", command=self.logout, tooltip_text="Logout (Ctrl+L)")
        logout_button.pack(side=tk.RIGHT, padx=5)

        # --- Statistics Frames ---
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        # --- Style Configuration ---
        style = ttk.Style(self)
        style.configure("Green.TLabel", foreground="green")
        style.configure("Orange.TLabel", foreground="orange")
        style.configure("Red.TLabel", foreground="red")

        # Total Sales Today
        sales_labelframe = ttk.LabelFrame(stats_frame, text="✔ Total Sales Today")
        sales_labelframe.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.sales_label = ttk.Label(sales_labelframe, text="0.00 LKR", font=("Arial", 24), style="Green.TLabel")
        self.sales_label.pack(padx=20, pady=20)

        # Near Expiry Items
        expiry_labelframe = ttk.LabelFrame(stats_frame, text="⚠ Items Nearing Expiry (30 days)", cursor="hand2")
        expiry_labelframe.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.expiry_label = ttk.Label(expiry_labelframe, text="0 Items", font=("Arial", 24), style="Orange.TLabel")
        self.expiry_label.pack(padx=20, pady=20)
        expiry_labelframe.bind("<Button-1>", self.show_near_expiry_details)
        self.expiry_label.bind("<Button-1>", self.show_near_expiry_details)


        # Low Stock Alerts
        stock_labelframe = ttk.LabelFrame(stats_frame, text="🔥 Low Stock Alerts", cursor="hand2")
        stock_labelframe.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.stock_label = ttk.Label(stock_labelframe, text="0 Items", font=("Arial", 24), style="Red.TLabel")
        self.stock_label.pack(padx=20, pady=20)
        stock_labelframe.bind("<Button-1>", self.show_low_stock_details)
        self.stock_label.bind("<Button-1>", self.show_low_stock_details)

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
        self.app_controller.show_login_frame()

    def show_user_management_view(self):
        """Shows the user management view."""
        if self.user_info['role'] != 'Admin':
            messagebox.showerror("Access Denied", "You do not have permission to access this feature.")
            return

        if self.app_controller.current_frame:
            self.app_controller.current_frame.destroy()

        self.app_controller.current_frame = UserManagementView(self.parent, self.user_info, self.app_controller)
        self.app_controller.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_not_implemented(self):
        """Shows a 'Feature not implemented' message."""
        messagebox.showinfo("Info", "This feature is not yet implemented.")
