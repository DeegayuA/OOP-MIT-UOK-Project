import tkinter as tk
from tkinter import ttk, messagebox
import services
from gui.base_window import BaseWindow
from gui.widgets.datepicker import create_datepicker_entry

class InventoryView(BaseWindow):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller

        self.create_widgets()
        self.refresh_products()

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

        # --- Action Buttons (Bottom Frame) ---
        ttk.Button(button_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Product", command=self.edit_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Batch", command=self.add_batch).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Batch", command=self.delete_batch).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back to Dashboard", command=self.app_controller.show_main_dashboard).pack(side=tk.RIGHT, padx=5)

    def refresh_products(self):
        self.all_products = services.get_all_products()
        self.filter_products()

    def filter_products(self, event=None):
        search_term = self.product_search_var.get().lower()

        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        for i in self.batches_tree.get_children():
            self.batches_tree.delete(i)

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
        product_name = self.products_tree.item(selected_item[0])['values'][1]

        win = AddBatchWindow(self, product_name)
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
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.EW)
        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(form_frame, textvariable=self.category_var, values=["Water", "Soft Drink"]).grid(row=1, column=1, sticky=tk.EW)
        ttk.Label(form_frame, text="Reorder Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(form_frame, from_=0, to=1000, textvariable=self.reorder_level_var).grid(row=2, column=1, sticky=tk.EW)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

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
    def __init__(self, parent, product_name):
        super().__init__(parent)
        self.title(f"Add Batch for {product_name}")
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
        ttk.Entry(form_frame, textvariable=self.batch_number_var).grid(row=0, column=1, sticky=tk.EW, pady=2)

        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(form_frame, textvariable=self.quantity_var).grid(row=1, column=1, sticky=tk.EW, pady=2)

        # Manufacture Date
        mfg_date_frame, self.mfg_date_entry = create_datepicker_entry(form_frame, "Manufacture Date:")
        mfg_date_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

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
