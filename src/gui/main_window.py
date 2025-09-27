import tkinter as tk
from tkinter import ttk, messagebox
from services import get_dashboard_stats, get_near_expiry_items, get_low_stock_items, get_recent_sales
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
        # Header frame for greeting and navigation
        header_frame = ttk.Frame(self)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Welcome message
        welcome_text = f"Welcome, {self.user_info.get('username', 'User')}!"
        welcome_label = ttk.Label(header_frame, text=welcome_text, font=("Arial", 14, "bold"))
        welcome_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Navigation buttons in the header
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        inventory_button = TooltipButton(nav_frame, text="Inventory", command=self.app_controller.show_inventory_view, tooltip_text="Manage Products (Ctrl+I)")
        inventory_button.pack(side=tk.LEFT, padx=5)

        sales_button = TooltipButton(nav_frame, text="Sales", command=self.app_controller.show_sales_view, tooltip_text="New Sale (Ctrl+S)")
        sales_button.pack(side=tk.LEFT, padx=5)

        orders_button = TooltipButton(nav_frame, text="Orders", command=self.app_controller.show_order_view, tooltip_text="Manage Orders (Ctrl+O)")
        orders_button.pack(side=tk.LEFT, padx=5)

        reports_button = TooltipButton(nav_frame, text="Reports", command=self.app_controller.show_reports_view, tooltip_text="View Reports (Ctrl+R)")
        reports_button.pack(side=tk.LEFT, padx=5)

        if self.user_info['role'] == 'Admin':
            users_button = TooltipButton(nav_frame, text="Users", command=self.show_user_management_view, tooltip_text="Manage Users")
            users_button.pack(side=tk.LEFT, padx=5)

        if self.user_info['role'] == 'Viewer':
            sales_button.configure(state=tk.DISABLED)
            orders_button.configure(state=tk.DISABLED)

        help_button = TooltipButton(nav_frame, text="Help", command=self.app_controller.show_help_window, tooltip_text="Get Help (Ctrl+H)")
        help_button.pack(side=tk.LEFT, padx=5)

        logout_button = TooltipButton(nav_frame, text="Logout", command=self.logout, tooltip_text="Logout (Ctrl+L)")
        logout_button.pack(side=tk.LEFT, padx=5)

        # Main content area
        main_content = ttk.Frame(self, style="Card.TFrame", padding=10)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        main_content.grid_columnconfigure((0, 1, 2), weight=1)
        main_content.grid_rowconfigure(0, weight=1)

        # --- Statistics Frames ---
        stats_frame = main_content

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

        # Add cursor pointer for expiry items
        self.expiry_label.configure(cursor="hand2")
        # Low Stock Alerts
        stock_labelframe = ttk.LabelFrame(stats_frame, text="🔥 Low Stock Alerts", cursor="hand2")
        stock_labelframe.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.stock_label = ttk.Label(stock_labelframe, text="0 Items", font=("Arial", 24), style="Red.TLabel")
        self.stock_label.pack(padx=20, pady=20)
        stock_labelframe.bind("<Button-1>", self.show_low_stock_details)
        self.stock_label.bind("<Button-1>", self.show_low_stock_details)

        # These settings are already defined above
        main_content.grid_rowconfigure(1, weight=1)
        
        # Create tables frame for the second row
        tables_frame = ttk.Frame(main_content)
        tables_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=3, pady=5)
        tables_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Recent Sales Table
        sales_table_frame = ttk.LabelFrame(tables_frame, text="Recent Sales")
        sales_table_frame.grid(row=0, column=0, sticky="nsew", padx=3, pady=5)
        self.sales_tree = ttk.Treeview(sales_table_frame, columns=("sale_id", "date", "customer", "amount"), show="headings", height=5)
        self.sales_tree.heading("sale_id", text="Sale ID")
        self.sales_tree.heading("date", text="Date")
        self.sales_tree.heading("customer", text="Customer")
        self.sales_tree.heading("amount", text="Amount")
        self.sales_tree.pack(fill="both", expand=True, padx=3, pady=5)
        
        # Near Expiry Table
        expiry_table_frame = ttk.LabelFrame(tables_frame, text="Nearing Expiry")
        expiry_table_frame.grid(row=0, column=1, sticky="nsew", padx=3, pady=5)
        self.expiry_tree = ttk.Treeview(expiry_table_frame, columns=("product", "batch", "qty", "expiry_date"), show="headings", height=5)
        self.expiry_tree.heading("product", text="Product")
        self.expiry_tree.heading("batch", text="Batch")
        self.expiry_tree.heading("qty", text="Quantity")
        self.expiry_tree.heading("expiry_date", text="Expiry Date")
        self.expiry_tree.pack(fill="both", expand=True, padx=3, pady=5)
        
        # Low Stock Table
        low_stock_table_frame = ttk.LabelFrame(tables_frame, text="Low Stock")
        low_stock_table_frame.grid(row=0, column=2, sticky="nsew", padx=3, pady=5)
        self.low_stock_tree = ttk.Treeview(low_stock_table_frame, columns=("product", "stock", "reorder_level"), show="headings", height=5)
        self.low_stock_tree.heading("product", text="Product")
        self.low_stock_tree.heading("stock", text="Stock")
        self.low_stock_tree.heading("reorder_level", text="Reorder Level")
        self.low_stock_tree.pack(fill="both", expand=True, padx=3, pady=5)

    def update_stats(self):
        """Fetches stats from the service layer and updates the UI."""
        try:
            stats = get_dashboard_stats()
            self.sales_label.config(text=f"{stats['total_sales_today']:.2f} LKR")
            self.expiry_label.config(text=f"{stats['near_expiry_items']} Items")
            self.stock_label.config(text=f"{stats['low_stock_items']} Items")
            self.update_tables()
        except Exception as e:
            print(f"Error updating dashboard stats: {e}")
            # Optionally show an error message in the UI
            self.sales_label.config(text="Error")
            self.expiry_label.config(text="Error")
            self.stock_label.config(text="Error")

    def update_tables(self):
        """Fetches data and populates the dashboard tables."""
        try:
            # Clear existing data
            for tree in [self.sales_tree, self.expiry_tree, self.low_stock_tree]:
                tree.delete(*tree.get_children())

            # Populate Recent Sales
            recent_sales = get_recent_sales()
            for sale in recent_sales:
                self.sales_tree.insert("", "end", values=(
                    sale['sale_id'],
                    sale['sale_date'],
                    sale['customer_name'] or "N/A",
                    f"{sale['total_amount']:.2f} LKR"
                ))

            # Populate Near Expiry Items
            near_expiry_items = get_near_expiry_items()
            for item in near_expiry_items:
                self.expiry_tree.insert("", "end", values=(
                    item['name'],
                    item['batch_number'],
                    item['quantity'],
                    item['expiry_date']
                ))

            # Populate Low Stock Items
            low_stock_items = get_low_stock_items()
            for item in low_stock_items:
                self.low_stock_tree.insert("", "end", values=(
                    item['name'],
                    item['total_stock'],
                    item['reorder_level']
                ))

        except Exception as e:
            print(f"Error updating dashboard tables: {e}")
            messagebox.showerror("Error", "Could not update dashboard tables.")

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




