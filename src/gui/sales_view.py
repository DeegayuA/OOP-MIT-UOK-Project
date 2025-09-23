import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import services
from .widgets.tooltip_button import TooltipButton

class SalesView(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.cart = [] # List of {'product_id':, 'name':, 'quantity':, 'price':}
        self.customers = [] # To store full customer objects

        self.create_widgets()
        self.load_initial_data()
        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.bind("<Control-Return>", lambda event: self.add_to_cart())
        self.bind("<Control-e>", lambda event: self.edit_cart_item_quantity())
        self.cart_tree.bind("<Delete>", lambda event: self.remove_from_cart())
        self.bind("<Control-s>", lambda event: self.finalize_sale())
        self.bind("<Escape>", lambda event: self.app_controller.show_main_dashboard())

    def create_widgets(self):
        # --- Main Layout ---
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X)
        middle_frame = ttk.Frame(self, padding="10")
        middle_frame.pack(fill=tk.BOTH, expand=True)
        bottom_frame = ttk.Frame(self, padding="10")
        bottom_frame.pack(fill=tk.X)

        # --- Top Frame: Customer Selection ---
        ttk.Label(top_frame, text="Customer:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.customer_var = tk.StringVar()
        self.customer_menu = ttk.Combobox(top_frame, textvariable=self.customer_var, state="readonly")
        self.customer_menu.pack(side=tk.LEFT, padx=10)

        # --- Middle Frame: Products and Cart ---
        products_frame = ttk.LabelFrame(middle_frame, text="Available Products")
        products_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        search_bar_frame = ttk.Frame(products_frame)
        search_bar_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Label(search_bar_frame, text="Search:").pack(side=tk.LEFT)
        self.product_search_var = tk.StringVar()
        product_search_entry = ttk.Entry(search_bar_frame, textvariable=self.product_search_var)
        product_search_entry.pack(fill=tk.X, expand=True)
        product_search_entry.bind("<KeyRelease>", self.filter_products)

        cart_frame = ttk.LabelFrame(middle_frame, text="Current Sale")
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.products_tree = ttk.Treeview(products_frame, columns=("id", "name", "price", "stock"), show="headings")
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Product")
        self.products_tree.heading("price", text="Price")
        self.products_tree.heading("stock", text="Stock")
        self.products_tree.column("id", width=40, stretch=False)
        self.products_tree.column("stock", width=60, stretch=False)
        self.products_tree.pack(fill=tk.BOTH, expand=True)

        TooltipButton(products_frame, text="Add to Cart (Ctrl+Enter)", command=self.add_to_cart).pack(pady=5)

        self.cart_tree = ttk.Treeview(cart_frame, columns=("id", "name", "qty", "total"), show="headings")
        self.cart_tree.heading("id", text="ID")
        self.cart_tree.heading("name", text="Product")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("total", text="Total")
        self.cart_tree.column("id", width=40); self.cart_tree.column("qty", width=50); self.cart_tree.column("total", width=80)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        cart_button_frame = ttk.Frame(cart_frame)
        cart_button_frame.pack(pady=5)
        TooltipButton(cart_button_frame, text="Edit Qty (Ctrl+E)", command=self.edit_cart_item_quantity).pack(side=tk.LEFT, padx=5)
        TooltipButton(cart_button_frame, text="Remove (Del)", command=self.remove_from_cart).pack(side=tk.LEFT, padx=5)

        # --- Bottom Frame: Totals and Finalize ---
        totals_frame = ttk.Frame(bottom_frame)
        totals_frame.pack(side=tk.RIGHT)
        self.total_label = ttk.Label(totals_frame, text="Total: 0.00 LKR", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=5)

        TooltipButton(bottom_frame, text="Finalize Sale (Ctrl+S)", command=self.finalize_sale).pack(side=tk.LEFT, ipady=10)
        TooltipButton(bottom_frame, text="Back (Esc)", command=self.app_controller.show_main_dashboard).pack(side=tk.LEFT, padx=20)

    def load_initial_data(self):
        # Load customers
        self.customers = services.get_all_customers()
        customer_names = ["Walk-in Customer"] + [c['name'] for c in self.customers]
        self.customer_menu['values'] = customer_names
        self.customer_menu.set("Walk-in Customer")
        # Load products
        self.refresh_products_list()

    def load_initial_data(self):
        # Load customers
        self.customers = services.get_all_customers()
        customer_names = ["Walk-in Customer"] + [c['name'] for c in self.customers]
        self.customer_menu['values'] = customer_names
        self.customer_menu.set("Walk-in Customer")
        # Load products
        self.all_products = []
        self.refresh_products_list()

    def refresh_products_list(self):
        self.all_products = services.get_products_for_sale()
        self.filter_products()

    def filter_products(self, event=None):
        search_term = self.product_search_var.get().lower()

        for i in self.products_tree.get_children():
            self.products_tree.delete(i)

        for p in self.all_products:
            if search_term in p['name'].lower():
                self.products_tree.insert("", "end", values=(
                    p['product_id'],
                    p['name'],
                    f"{p['selling_price']:.2f} LKR",
                    p['total_stock']
                ))

    def add_to_cart(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to add.")
            return

        item_values = self.products_tree.item(selected_item[0])['values']
        product_id, name, price_str = item_values
        price = float(price_str.replace(" LKR", "").replace(",", ""))

        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {name}:", parent=self, minvalue=1)
        if not quantity:
            return

        # Check if item is already in cart, if so, update quantity
        for item in self.cart:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                break
        else: # If loop doesn't break, item is not in cart
            self.cart.append({'product_id': product_id, 'name': name, 'quantity': quantity, 'price': price})

        self.update_cart_display()

    def remove_from_cart(self):
        selected_item = self.cart_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item from the cart to remove.")
            return

        item_id = int(self.cart_tree.item(selected_item[0])['values'][0])

        # Find and remove the item from the self.cart list
        self.cart = [item for item in self.cart if item['product_id'] != item_id]

        self.update_cart_display()

    def edit_cart_item_quantity(self):
        selected_item = self.cart_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item from the cart to edit.")
            return

        item_values = self.cart_tree.item(selected_item[0])['values']
        product_id = int(item_values[0])
        product_name = item_values[1]

        new_quantity = simpledialog.askinteger("Edit Quantity", f"Enter new quantity for {product_name}:", parent=self, minvalue=1)

        if new_quantity:
            for item in self.cart:
                if item['product_id'] == product_id:
                    item['quantity'] = new_quantity
                    break
            self.update_cart_display()

    def update_cart_display(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)

        total = 0
        for item in self.cart:
            item_total = item['quantity'] * item['price']
            total += item_total
            self.cart_tree.insert("", "end", values=(item['product_id'], item['name'], item['quantity'], f"{item_total:.2f} LKR"))

        self.total_label.config(text=f"Total: {total:.2f} LKR")

    def finalize_sale(self):
        if not self.cart:
            messagebox.showerror("Cart Error", "Cannot finalize an empty sale.")
            return

        # Get customer ID
        selected_customer_name = self.customer_var.get()
        customer_id = None
        if selected_customer_name != "Walk-in Customer":
            customer = next((c for c in self.customers if c['name'] == selected_customer_name), None)
            if customer:
                customer_id = customer['customer_id']

        user_id = self.app_controller.current_user['user_id']

        try:
            sale_id = services.create_sale(user_id, customer_id, self.cart)
            messagebox.showinfo("Success", f"Sale #{sale_id} created successfully!")
            self.reset_sale()
        except ValueError as e:
            messagebox.showerror("Stock Error", str(e))
        except Exception as e:
            messagebox.showerror("Sale Error", f"An error occurred: {e}")

    def reset_sale(self):
        self.cart = []
        self.update_cart_display()
        self.refresh_products_list()
        self.customer_menu.set("Walk-in Customer")
        self.app_controller.show_main_dashboard() # Go back to dashboard
