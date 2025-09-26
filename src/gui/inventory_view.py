import tkinter as tk
from tkinter import ttk, messagebox
import services
from gui.base_window import BaseWindow
from gui.widgets.datepicker import create_datepicker_entry
from gui.widgets.tooltip_button import TooltipButton
from datetime import date, timedelta

class InventoryView(BaseWindow):
    def __init__(self, parent, user_info, app_controller):
        super().__init__(parent)
        self.user_info = user_info
        self.app_controller = app_controller
        self._search_job = None

        self.create_widgets()
        self.refresh_products()
        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.bind("<Control-a>", lambda event: self.add_product())
        self.bind("<Control-e>", lambda event: self.edit_product())
        self.bind("<Control-b>", lambda event: self.add_batch())
        self.bind("<Escape>", lambda event: self.app_controller.show_main_dashboard())

    def create_widgets(self):
        # Main layout frames
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # --- Products List (Left Frame) ---
        product_header_frame = ttk.Frame(left_frame)
        product_header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(product_header_frame, text="Products", font=("Arial", 16)).pack(side=tk.LEFT)

        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.product_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.product_search_var)
        search_entry.pack(fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.filter_products)

        self.products_tree = ttk.Treeview(left_frame, columns=("id", "name", "category"), show="headings")
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Name")
        self.products_tree.heading("category", text="Category")
        self.products_tree.column("id", width=50, stretch=False)
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        self.products_tree.bind("<Delete>", lambda event: self.delete_product())

        # --- Batches List (Right Frame) ---
        ttk.Label(right_frame, text="Batches for Selected Product", font=("Arial", 16)).pack(pady=5)

        self.batches_tree = ttk.Treeview(
            right_frame,
            columns=("batch_id", "batch_no", "qty", "expiry", "sell_price"),
            show="headings"
        )
        self.batches_tree.heading("batch_id", text="ID")
        self.batches_tree.heading("batch_no", text="Batch No.")
        self.batches_tree.heading("qty", text="Quantity")
        self.batches_tree.heading("expiry", text="Expiry Date")
        self.batches_tree.heading("sell_price", text="Price")
        self.batches_tree.column("batch_id", width=50, stretch=False)
        self.batches_tree.pack(fill=tk.BOTH, expand=True)
        self.batches_tree.bind("<Delete>", lambda event: self.delete_batch())

        # --- Action Buttons (Bottom Frame) ---
        add_product_button = TooltipButton(button_frame, text="Add Product (Ctrl+A)", command=self.add_product)
        add_product_button.pack(side=tk.LEFT, padx=5)
        edit_product_button = TooltipButton(button_frame, text="Edit Product (Ctrl+E)", command=self.edit_product)
        edit_product_button.pack(side=tk.LEFT, padx=5)
        delete_product_button = TooltipButton(button_frame, text="Delete Product (Del)", command=self.delete_product)
        delete_product_button.pack(side=tk.LEFT, padx=5)
        add_batch_button = TooltipButton(button_frame, text="Add Batch (Ctrl+B)", command=self.add_batch)
        add_batch_button.pack(side=tk.LEFT, padx=5)
        delete_batch_button = TooltipButton(button_frame, text="Delete Batch (Del)", command=self.delete_batch)
        delete_batch_button.pack(side=tk.LEFT, padx=5)
        TooltipButton(button_frame, text="Back (Esc)", command=self.app_controller.show_main_dashboard).pack(side=tk.RIGHT, padx=5)

        if self.user_info['role'] in ['Viewer', 'Seller']:
            add_product_button.configure(state=tk.DISABLED)
            edit_product_button.configure(state=tk.DISABLED)
            delete_product_button.configure(state=tk.DISABLED)
            add_batch_button.configure(state=tk.DISABLED)
            delete_batch_button.configure(state=tk.DISABLED)

    def refresh_products(self):
        self.all_products = services.get_all_products()
        self.filter_products()

    def filter_products(self, event=None):
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(300, self._perform_filter)

    def _perform_filter(self):
        search_term = self.product_search_var.get().lower()

        self.products_tree.delete(*self.products_tree.get_children())
        self.batches_tree.delete(*self.batches_tree.get_children())

        for p in self.all_products:
            if search_term in p['name'].lower() or search_term in p['category'].lower():
                self.products_tree.insert("", tk.END, values=(p['product_id'], p['name'], p['category']))

    def on_product_select(self, event):
        for i in self.batches_tree.get_children():
            self.batches_tree.delete(i)

        selected_item = self.products_tree.selection()
        if not selected_item:
            return

        product_id = self.products_tree.item(selected_item[0])['values'][0]
        batches = services.get_batches_for_product(product_id)
        for b in batches:
            self.batches_tree.insert("", tk.END, values=(b['batch_id'], b['batch_number'], b['quantity'], b['expiry_date'], f"{b['selling_price']:.2f}LKR"))

    def add_product(self):
        win = AddEditProductWindow(self)
        self.wait_window(win)
        if win.result:
            try:
                services.add_product(**win.result)
                messagebox.showinfo("Success", "Product added successfully.")
                self.refresh_products()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {e}")

    def edit_product(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to edit.")
            return

        product_id = self.products_tree.item(selected_item[0])['values'][0]
        product_data = services.get_product_by_id(product_id)

        if not product_data:
            messagebox.showerror("Error", "Could not fetch product details.")
            return

        win = AddEditProductWindow(self, product=product_data)
        self.wait_window(win)
        if win.result:
            try:
                services.update_product(win.result['id'], win.result['name'], win.result['category'], win.result['reorder_level'])
                messagebox.showinfo("Success", "Product updated successfully.")
                self.refresh_products()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")

    def delete_product(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to delete.")
            return

        item_values = self.products_tree.item(selected_item[0])['values']
        product_id = item_values[0]
        product_name = item_values[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'? This will also delete all its batches."):
            try:
                services.delete_product(product_id)
                messagebox.showinfo("Success", "Product deleted successfully.")
                self.refresh_products()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {e}")

    def add_batch(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to add a batch for.")
            return

        product_id = self.products_tree.item(selected_item[0])['values'][0]
        product = services.get_product_by_id(product_id)
        if not product:
            messagebox.showerror("Error", "Could not fetch product details.")
            return

        win = AddBatchWindow(self, product)
        self.wait_window(win)
        if win.result:
            try:
                services.add_batch(product_id, win.result)
                messagebox.showinfo("Success", "Batch added successfully.")
                self.on_product_select(None) # Refresh batch list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add batch: {e}")

    def delete_batch(self):
        selected_item = self.batches_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a batch to delete.")
            return

        item_values = self.batches_tree.item(selected_item[0])['values']
        batch_id = item_values[0]
        batch_no = item_values[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete batch '{batch_no}'?"):
            try:
                services.delete_batch(batch_id)
                messagebox.showinfo("Success", "Batch deleted successfully.")
                self.on_product_select(None) # Refresh batch list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete batch: {e}")

class AddEditProductWindow(BaseWindow):
    def __init__(self, parent, product=None):
        super().__init__(parent)
        self.product = product
        self.result = None
        self.title("Edit Product" if product else "Add New Product")
        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        self.name_var = tk.StringVar(value=self.product['name'] if self.product else "")
        self.category_var = tk.StringVar(value=self.product['category'] if self.product else "Water")
        self.reorder_level_var = tk.IntVar(value=self.product['reorder_level'] if self.product else 10)

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Product Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var)
        name_entry.grid(row=0, column=1, sticky=tk.EW)
        name_entry.focus_set()
        name_entry.bind("<Return>", lambda event: self.on_save())

        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_combobox = ttk.Combobox(form_frame, textvariable=self.category_var, values=services.PRODUCT_CATEGORIES)
        category_combobox.grid(row=1, column=1, sticky=tk.EW)
        category_combobox.bind("<Return>", lambda event: self.on_save())
        ttk.Label(form_frame, text="Reorder Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(form_frame, from_=0, to=1000, textvariable=self.reorder_level_var).grid(row=2, column=1, sticky=tk.EW)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        self.bind("<Control-s>", lambda event: self.on_save())

    def on_save(self):
        name = self.name_var.get()
        if not name:
            messagebox.showerror("Validation Error", "Product name cannot be empty.")
            return
        self.result = {"name": name, "category": self.category_var.get(), "reorder_level": self.reorder_level_var.get()}
        if self.product:
            self.result["id"] = self.product["product_id"]
        self.destroy()

class AddBatchWindow(BaseWindow):
    def __init__(self, parent, product):
        super().__init__(parent)
        self.product = product
        self.title(f"Add Batch for {self.product['name']}")
        self.result = None
        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        self.batch_number_var = tk.StringVar()
        self.quantity_var = tk.IntVar()
        self.batch_number_var = tk.StringVar()
        self.quantity_var = tk.IntVar()
        self.cost_price_var = tk.DoubleVar()
        self.sell_price_var = tk.DoubleVar()

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.grid_columnconfigure(1, weight=1)

        # Batch Number
        ttk.Label(form_frame, text="Batch Number:").grid(row=0, column=0, sticky=tk.W, pady=2)
        batch_entry = ttk.Entry(form_frame, textvariable=self.batch_number_var)
        batch_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        batch_entry.focus_set()
        batch_entry.bind("<Return>", lambda event: self.on_save())

        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.W, pady=2)
        quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var)
        quantity_entry.grid(row=1, column=1, sticky=tk.EW, pady=2)
        quantity_entry.bind("<Return>", lambda event: self.on_save())

        # Manufacture Date
        mfg_date_frame, self.mfg_date_entry = create_datepicker_entry(form_frame, "Manufacture Date:")
        mfg_date_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.mfg_date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.mfg_date_entry.bind("<<DatepickerSelected>>", self._calculate_and_set_expiry)

        # Expiry Date
        exp_date_frame, self.exp_date_entry = create_datepicker_entry(form_frame, "Expiry Date:")
        exp_date_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Cost Price
        ttk.Label(form_frame, text="Cost Price:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(form_frame, textvariable=self.cost_price_var).grid(row=4, column=1, sticky=tk.EW, pady=2)

        # Selling Price
        ttk.Label(form_frame, text="Selling Price:").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(form_frame, textvariable=self.sell_price_var).grid(row=5, column=1, sticky=tk.EW, pady=2)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        self.bind("<Control-s>", lambda event: self.on_save())

        # Set initial expiry date
        self._calculate_and_set_expiry()

    def _calculate_and_set_expiry(self, event=None):
        try:
            mfg_date_str = self.mfg_date_entry.get()
            mfg_date = date.fromisoformat(mfg_date_str)

            years_to_add = 1 # Default
            if self.product['category'] == 'Water':
                years_to_add = 2
            elif self.product['category'] == 'Soft Drink':
                years_to_add = 1

            expiry_date = mfg_date + timedelta(days=365 * years_to_add)

            self.exp_date_entry.delete(0, tk.END)
            self.exp_date_entry.insert(0, expiry_date.strftime('%Y-%m-%d'))
        except (ValueError, TypeError):
            # Handle cases where the date string is invalid or empty
            self.exp_date_entry.delete(0, tk.END)

    def on_save(self):
        # Simple validation
        if not all([self.batch_number_var.get(), self.quantity_var.get(), self.exp_date_entry.get(), self.sell_price_var.get()]):
            messagebox.showerror("Validation Error", "Please fill in all required fields.")
            return
        self.result = {
            "batch_number": self.batch_number_var.get(),
            "quantity": self.quantity_var.get(),
            "manufacture_date": self.mfg_date_entry.get() or None,
            "expiry_date": self.exp_date_entry.get(),
            "cost_price": self.cost_price_var.get(),
            "selling_price": self.sell_price_var.get()
        }
        self.destroy()
