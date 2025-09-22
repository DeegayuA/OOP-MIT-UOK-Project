import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import services

class SalesView(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.cart = [] # List of {'product_id':, 'name':, 'quantity':, 'price':}
        self.customers = [] # To store full customer objects

        self.create_widgets()
        self.load_initial_data()

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
        cart_frame = ttk.LabelFrame(middle_frame, text="Current Sale")
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.products_tree = ttk.Treeview(products_frame, columns=("id", "name", "price"), show="headings")
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Product")
        self.products_tree.heading("price", text="Price")
        self.products_tree.column("id", width=40)
        self.products_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(products_frame, text="Add to Cart ->", command=self.add_to_cart).pack(pady=5)

        self.cart_tree = ttk.Treeview(cart_frame, columns=("id", "name", "qty", "total"), show="headings")
        self.cart_tree.heading("id", text="ID")
        self.cart_tree.heading("name", text="Product")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("total", text="Total")
        self.cart_tree.column("id", width=40); self.cart_tree.column("qty", width=50); self.cart_tree.column("total", width=80)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        # --- Bottom Frame: Totals and Finalize ---
        totals_frame = ttk.Frame(bottom_frame)
        totals_frame.pack(side=tk.RIGHT)
        self.total_label = ttk.Label(totals_frame, text="Total: $0.00", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=5)

        ttk.Button(bottom_frame, text="Finalize Sale", command=self.finalize_sale).pack(side=tk.LEFT, ipady=10)
        ttk.Button(bottom_frame, text="Back to Dashboard", command=self.app_controller.show_main_dashboard).pack(side=tk.LEFT, padx=20)

    def load_initial_data(self):
        # Load customers
        self.customers = services.get_all_customers()
        customer_names = ["Walk-in Customer"] + [c['name'] for c in self.customers]
        self.customer_menu['values'] = customer_names
        self.customer_menu.set("Walk-in Customer")
        # Load products
        self.refresh_products_list()

    def refresh_products_list(self):
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        products = services.get_products_for_sale()
        for p in products:
            self.products_tree.insert("", "end", values=(p['product_id'], p['name'], f"${p['selling_price']:.2f}"))

    def add_to_cart(self):
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to add.")
            return

        item_values = self.products_tree.item(selected_item[0])['values']
        product_id, name, price_str = item_values
        price = float(price_str.replace("$", ""))

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

    def update_cart_display(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)

        total = 0
        for item in self.cart:
            item_total = item['quantity'] * item['price']
            total += item_total
            self.cart_tree.insert("", "end", values=(item['product_id'], item['name'], item['quantity'], f"${item_total:.2f}"))

        self.total_label.config(text=f"Total: ${total:.2f}")

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
        self.app_controller.current_frame.update_stats() # Refresh dashboard stats
