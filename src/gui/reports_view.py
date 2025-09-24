import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import services
from .widgets.tooltip_button import TooltipButton
import threading
import queue

class ReportsView(tk.Frame):
    def __init__(self, parent, user_info, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info
        self.app_controller = app_controller
        self.report_queue = queue.Queue()

        self.create_widgets()

    def create_widgets(self):
        # --- Main Layout ---
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X)

        self.report_content_frame = ttk.Frame(self, padding="10")
        self.report_content_frame.pack(fill=tk.BOTH, expand=True)

        bottom_frame = ttk.Frame(self, padding="10")
        bottom_frame.pack(fill=tk.X)

        # --- Top Frame: Controls ---
        ttk.Label(top_frame, text="Select Report:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0, 10))

        self.report_type_var = tk.StringVar()
        self.report_type_menu = ttk.Combobox(top_frame, textvariable=self.report_type_var, state="readonly", width=30)
        self.report_type_menu['values'] = ["Sales Report", "Product Performance Report", "Inventory Report"]
        self.report_type_menu.pack(side=tk.LEFT)
        self.report_type_menu.bind("<<ComboboxSelected>>", self.on_report_type_change)

        # --- Bottom Frame: Navigation ---
        TooltipButton(bottom_frame, text="Back to Dashboard (Esc)", command=self.app_controller.show_main_dashboard).pack(side=tk.LEFT)

    def on_report_type_change(self, event=None):
        # Clear previous report content
        for widget in self.report_content_frame.winfo_children():
            widget.destroy()

        report_type = self.report_type_var.get()

        if report_type == "Sales Report":
            self.create_sales_report_view()
        elif report_type == "Product Performance Report":
            self.create_product_performance_report_view()
        elif report_type == "Inventory Report":
            self.create_inventory_report_view()

    def create_sales_report_view(self):
        """Creates the UI components for the Sales Report."""
        controls_frame = ttk.Frame(self.report_content_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        ttk.Label(controls_frame, text="Start Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_date_entry = DateEntry(controls_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(controls_frame, text="End Date:").pack(side=tk.LEFT, padx=(10, 5))
        self.end_date_entry = DateEntry(controls_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)

        self.sales_generate_button = TooltipButton(controls_frame, text="Generate Report", command=self.generate_sales_report)
        self.sales_generate_button.pack(side=tk.LEFT, padx=10)

        # --- Treeview for displaying sales ---
        tree_frame = ttk.Frame(self.report_content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.sales_tree = ttk.Treeview(tree_frame, columns=("id", "date", "cashier", "customer", "discount", "total"), show="headings")
        self.sales_tree.heading("id", text="Sale ID")
        self.sales_tree.heading("date", text="Date")
        self.sales_tree.heading("cashier", text="Cashier")
        self.sales_tree.heading("customer", text="Customer")
        self.sales_tree.heading("discount", text="Discount")
        self.sales_tree.heading("total", text="Total")

        self.sales_tree.column("id", width=60)
        self.sales_tree.column("date", width=150)
        self.sales_tree.column("cashier", width=120)
        self.sales_tree.column("customer", width=120)
        self.sales_tree.column("discount", width=80)
        self.sales_tree.column("total", width=100)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sales_tree.yview)
        vsb.pack(side='right', fill='y')
        self.sales_tree.configure(yscrollcommand=vsb.set)

        self.sales_tree.pack(fill=tk.BOTH, expand=True)

        # --- Summary Frame ---
        summary_frame = ttk.LabelFrame(self.report_content_frame, text="Summary")
        summary_frame.pack(fill=tk.X, pady=10)

        self.total_revenue_label = ttk.Label(summary_frame, text="Total Revenue: 0.00 LKR", font=("Arial", 12, "bold"))
        self.total_revenue_label.pack(anchor="w", padx=10)

        self.total_cogs_label = ttk.Label(summary_frame, text="Total COGS: 0.00 LKR", font=("Arial", 12, "bold"))
        self.total_cogs_label.pack(anchor="w", padx=10)

        self.gross_profit_label = ttk.Label(summary_frame, text="Gross Profit: 0.00 LKR", font=("Arial", 12, "bold"))
        self.gross_profit_label.pack(anchor="w", padx=10)

        self.sales_loading_label = ttk.Label(self.report_content_frame, text="", font=("Arial", 10, "italic"))
        self.sales_loading_label.pack(pady=5)

    def generate_sales_report(self):
        """Initiates the sales report generation in a background thread."""
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        if not start_date or not end_date or start_date > end_date:
            messagebox.showerror("Error", "Please select a valid date range.")
            return

        self.sales_generate_button.config(state=tk.DISABLED)
        self.sales_loading_label.config(text="Generating report, please wait...")

        # Clear previous data
        for i in self.sales_tree.get_children():
            self.sales_tree.delete(i)

        # Reset summary
        self.total_revenue_label.config(text="Total Revenue: 0.00 LKR")
        self.total_cogs_label.config(text="Total COGS: 0.00 LKR")
        self.gross_profit_label.config(text="Gross Profit: 0.00 LKR")

        thread = threading.Thread(target=self._fetch_sales_report_data, args=(start_date, end_date))
        thread.daemon = True
        thread.start()

        self.after(100, self._check_sales_queue)

    def _fetch_sales_report_data(self, start_date, end_date):
        """Worker function to fetch data from the database."""
        try:
            report_data = services.get_sales_report(start_date, end_date)
            summary_data = services.get_sales_summary(start_date, end_date)
            self.report_queue.put(("sales", (report_data, summary_data)))
        except Exception as e:
            self.report_queue.put(("error", str(e)))

    def _check_sales_queue(self):
        """Checks the queue for data and updates the UI."""
        try:
            message_type, data = self.report_queue.get_nowait()

            if message_type == "error":
                messagebox.showerror("Error", f"Failed to generate report: {data}")
            elif message_type == "sales":
                report_data, summary_data = data
                for row in report_data:
                    customer_name = row['customer_name'] if row['customer_name'] else "Walk-in"
                    self.sales_tree.insert("", "end", values=(
                        row['sale_id'],
                        row['sale_date'],
                        row['username'],
                        customer_name,
                        f"{row['discount_applied']:.2f}",
                        f"{row['total_amount']:.2f}"
                    ))

                total_revenue = summary_data.get('total_revenue', 0)
                total_cogs = summary_data.get('total_cogs', 0)
                gross_profit = total_revenue - total_cogs

                self.total_revenue_label.config(text=f"Total Revenue: {total_revenue:.2f} LKR")
                self.total_cogs_label.config(text=f"Total COGS: {total_cogs:.2f} LKR")
                self.gross_profit_label.config(text=f"Gross Profit: {gross_profit:.2f} LKR")

            # Clean up
            self.sales_loading_label.config(text="")
            self.sales_generate_button.config(state=tk.NORMAL)

        except queue.Empty:
            self.after(100, self._check_sales_queue)

    def create_product_performance_report_view(self):
        """Creates the UI components for the Product Performance Report."""
        controls_frame = ttk.Frame(self.report_content_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        ttk.Label(controls_frame, text="Start Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.prod_start_date_entry = DateEntry(controls_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.prod_start_date_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(controls_frame, text="End Date:").pack(side=tk.LEFT, padx=(10, 5))
        self.prod_end_date_entry = DateEntry(controls_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.prod_end_date_entry.pack(side=tk.LEFT, padx=5)

        self.prod_generate_button = TooltipButton(controls_frame, text="Generate Report", command=self.generate_product_performance_report)
        self.prod_generate_button.pack(side=tk.LEFT, padx=10)

        tree_frame = ttk.Frame(self.report_content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.product_tree = ttk.Treeview(tree_frame, columns=("id", "name", "category", "qty_sold", "revenue"), show="headings")
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("name", text="Product Name")
        self.product_tree.heading("category", text="Category")
        self.product_tree.heading("qty_sold", text="Quantity Sold")
        self.product_tree.heading("revenue", text="Total Revenue (LKR)")

        self.product_tree.column("id", width=50)
        self.product_tree.column("name", width=200)
        self.product_tree.column("category", width=100)
        self.product_tree.column("qty_sold", width=100)
        self.product_tree.column("revenue", width=150)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.product_tree.yview)
        vsb.pack(side='right', fill='y')
        self.product_tree.configure(yscrollcommand=vsb.set)
        self.product_tree.pack(fill=tk.BOTH, expand=True)

        self.prod_loading_label = ttk.Label(self.report_content_frame, text="", font=("Arial", 10, "italic"))
        self.prod_loading_label.pack(pady=5)

    def generate_product_performance_report(self):
        """Initiates the product performance report generation in a background thread."""
        start_date = self.prod_start_date_entry.get_date()
        end_date = self.prod_end_date_entry.get_date()

        if not start_date or not end_date or start_date > end_date:
            messagebox.showerror("Error", "Please select a valid date range.")
            return

        self.prod_generate_button.config(state=tk.DISABLED)
        self.prod_loading_label.config(text="Generating report, please wait...")

        for i in self.product_tree.get_children():
            self.product_tree.delete(i)

        thread = threading.Thread(target=self._fetch_product_performance_data, args=(start_date, end_date))
        thread.daemon = True
        thread.start()
        self.after(100, self._check_product_queue)

    def _fetch_product_performance_data(self, start_date, end_date):
        """Worker function to fetch product performance data."""
        try:
            report_data = services.get_product_performance_report(start_date, end_date)
            self.report_queue.put(("product", report_data))
        except Exception as e:
            self.report_queue.put(("error", str(e)))

    def _check_product_queue(self):
        """Checks the queue for product performance data and updates the UI."""
        try:
            message_type, data = self.report_queue.get_nowait()

            if message_type == "error":
                messagebox.showerror("Error", f"Failed to generate report: {data}")
            elif message_type == "product":
                for row in data:
                    self.product_tree.insert("", "end", values=(
                        row['product_id'],
                        row['product_name'],
                        row['category'],
                        row['total_quantity_sold'],
                        f"{row['total_revenue']:.2f}"
                    ))

            self.prod_loading_label.config(text="")
            self.prod_generate_button.config(state=tk.NORMAL)

        except queue.Empty:
            self.after(100, self._check_product_queue)

    def create_inventory_report_view(self):
        """Creates the UI components for the Inventory Report."""
        controls_frame = ttk.Frame(self.report_content_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        self.inv_generate_button = TooltipButton(controls_frame, text="Refresh Report", command=self.generate_inventory_report)
        self.inv_generate_button.pack(side=tk.LEFT)

        tree_frame = ttk.Frame(self.report_content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.inventory_tree = ttk.Treeview(tree_frame, columns=("id", "name", "category", "stock", "value"), show="headings")
        self.inventory_tree.heading("id", text="ID")
        self.inventory_tree.heading("name", text="Product Name")
        self.inventory_tree.heading("category", text="Category")
        self.inventory_tree.heading("stock", text="Total Stock")
        self.inventory_tree.heading("value", text="Total Stock Value (Cost)")

        self.inventory_tree.column("id", width=50)
        self.inventory_tree.column("name", width=200)
        self.inventory_tree.column("category", width=100)
        self.inventory_tree.column("stock", width=100)
        self.inventory_tree.column("value", width=150)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
        vsb.pack(side='right', fill='y')
        self.inventory_tree.configure(yscrollcommand=vsb.set)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)

        self.inv_loading_label = ttk.Label(self.report_content_frame, text="", font=("Arial", 10, "italic"))
        self.inv_loading_label.pack(pady=5)

        self.generate_inventory_report()

    def generate_inventory_report(self):
        """Initiates the inventory report generation in a background thread."""
        self.inv_generate_button.config(state=tk.DISABLED)
        self.inv_loading_label.config(text="Generating report, please wait...")

        for i in self.inventory_tree.get_children():
            self.inventory_tree.delete(i)

        thread = threading.Thread(target=self._fetch_inventory_report_data)
        thread.daemon = True
        thread.start()
        self.after(100, self._check_inventory_queue)

    def _fetch_inventory_report_data(self):
        """Worker function to fetch inventory data."""
        try:
            report_data = services.get_inventory_report()
            self.report_queue.put(("inventory", report_data))
        except Exception as e:
            self.report_queue.put(("error", str(e)))

    def _check_inventory_queue(self):
        """Checks the queue for inventory data and updates the UI."""
        try:
            message_type, data = self.report_queue.get_nowait()

            if message_type == "error":
                messagebox.showerror("Error", f"Failed to generate report: {data}")
            elif message_type == "inventory":
                for row in data:
                    self.inventory_tree.insert("", "end", values=(
                        row['product_id'],
                        row['name'],
                        row['category'],
                        row['total_stock'],
                        f"{row['total_cost_value']:.2f}"
                    ))

            self.inv_loading_label.config(text="")
            self.inv_generate_button.config(state=tk.NORMAL)

        except queue.Empty:
            self.after(100, self._check_inventory_queue)
