import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import services
from gui.base_window import BaseWindow
from .widgets.tooltip_button import TooltipButton

class OrderView(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.all_orders = []
        self.create_widgets()
        self.refresh_data()
        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda event: self.create_new_order())
        self.bind("<Control-u>", lambda event: self.update_status())
        self.bind("<Escape>", lambda event: self.app_controller.show_main_dashboard())

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Customer Orders", font=("Arial", 16)).pack(side=tk.LEFT, pady=5)

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search Customer:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.filter_orders)

        self.orders_tree = ttk.Treeview(main_frame, columns=("id", "customer", "date", "status"), show="headings")
        self.orders_tree.heading("id", text="Order ID"); self.orders_tree.heading("customer", text="Customer Name"); self.orders_tree.heading("date", text="Order Date"); self.orders_tree.heading("status", text="Status")
        self.orders_tree.column("id", width=80)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        TooltipButton(button_frame, text="New Order (Ctrl+N)", command=self.create_new_order).pack(side=tk.LEFT, padx=5)

        update_status_frame = ttk.Frame(button_frame)
        update_status_frame.pack(side=tk.LEFT, padx=10)
        self.status_var = tk.StringVar()
        status_menu = ttk.Combobox(update_status_frame, textvariable=self.status_var, state="readonly",
                                    values=['Received', 'Ready to Pack', 'Ready to Distribute', 'Completed'])
        status_menu.pack(side=tk.LEFT)
        TooltipButton(update_status_frame, text="Update Status (Ctrl+U)", command=self.update_status).pack(side=tk.LEFT, padx=5)

        TooltipButton(button_frame, text="Back (Esc)", command=self.app_controller.show_main_dashboard).pack(side=tk.RIGHT, padx=5)

    def refresh_data(self):
        self.all_orders = services.get_all_orders_with_customer_names()
        self.filter_orders()

    def filter_orders(self, event=None):
        search_term = self.search_var.get().lower()

        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)

        for o in self.all_orders:
            customer_name = o['customer_name'].lower() if o['customer_name'] else ""
            if search_term in customer_name:
                display_name = o['customer_name'] if o['customer_name'] else "N/A"
                self.orders_tree.insert("", tk.END, values=(o['order_id'], display_name, o['order_date'], o['status']))

    def update_status(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an order to update.")
            return

        new_status = self.status_var.get()
        if not new_status:
            messagebox.showwarning("Input Error", "Please select a status from the dropdown.")
            return

        order_id = self.orders_tree.item(selected_item[0])['values'][0]

        try:
            services.update_order_status(order_id, new_status)
            messagebox.showinfo("Success", "Order status updated successfully.")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {e}")

    def create_new_order(self):
        win = CreateOrderWindow(self)
        self.wait_window(win)
        if win.result:
            try:
                services.create_order(win.result['customer_id'], win.result['items'])
                messagebox.showinfo("Success", "Order created successfully.")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create order: {e}")


class CreateOrderWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create New Customer Order")
        self.geometry("600x400")
        self.result = None
        self.cart = []
        self.customers = services.get_all_customers()
        self.products = services.get_all_products() # Get all products for ordering
        self.create_widgets()
        self.filter_products()
        self.center_window()

    def create_widgets(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X)
        middle_frame = ttk.Frame(self, padding=10)
        middle_frame.pack(fill=tk.BOTH, expand=True)

        # Customer selection
        ttk.Label(top_frame, text="Customer:").pack(side=tk.LEFT)
        self.customer_var = tk.StringVar()
        customer_names = [c['name'] for c in self.customers]
        self.customer_menu = ttk.Combobox(top_frame, textvariable=self.customer_var, values=customer_names, state="readonly")
        self.customer_menu.pack(side=tk.LEFT, padx=5)
        self.customer_menu.focus_set()

        # Product selection and cart
        product_frame = ttk.LabelFrame(middle_frame, text="Add Products")
        product_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Search bar for products
        search_frame = ttk.Frame(product_frame)
        search_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.product_search_var = tk.StringVar()
        product_search_entry = ttk.Entry(search_frame, textvariable=self.product_search_var)
        product_search_entry.pack(fill=tk.X, expand=True)
        product_search_entry.bind("<KeyRelease>", self.filter_products)

        cart_frame = ttk.LabelFrame(middle_frame, text="Order Items")
        cart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(product_frame, text="Product:").pack()
        self.product_var = tk.StringVar()
        self.product_combobox = ttk.Combobox(product_frame, textvariable=self.product_var, state="readonly")
        self.product_combobox.pack(pady=5)

        ttk.Label(product_frame, text="Quantity:").pack()
        self.quantity_var = tk.IntVar(value=1)
        ttk.Spinbox(product_frame, from_=1, to=999, textvariable=self.quantity_var).pack(pady=5)
        TooltipButton(product_frame, text="Add to Order (Ctrl+Enter)", command=self.add_to_cart).pack(pady=10)

        self.cart_tree = ttk.Treeview(cart_frame, columns=("id", "name", "qty"), show="headings")
        self.cart_tree.heading("id", text="ID"); self.cart_tree.heading("name", text="Product"); self.cart_tree.heading("qty", text="Quantity")
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        self.cart_tree.bind("<Delete>", lambda e: self.remove_from_cart())

        cart_buttons_frame = ttk.Frame(cart_frame)
        cart_buttons_frame.pack(fill=tk.X, pady=5)
        TooltipButton(cart_buttons_frame, text="Edit Qty (Ctrl+E)", command=self.edit_quantity).pack(side=tk.LEFT)
        TooltipButton(cart_buttons_frame, text="Remove (Del)", command=self.remove_from_cart).pack(side=tk.LEFT, padx=5)

        # Bottom buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X)
        TooltipButton(button_frame, text="Save Order (Ctrl+S)", command=self.on_save).pack(side=tk.RIGHT, padx=5)
        TooltipButton(button_frame, text="Cancel (Esc)", command=self.destroy).pack(side=tk.RIGHT)
        self.bind("<Control-s>", lambda event: self.on_save())
        self.bind("<Escape>", lambda event: self.destroy())

    def add_to_cart(self):
        product_name = self.product_var.get()
        quantity = self.quantity_var.get()
        if not product_name or not quantity > 0:
            return

        product = next((p for p in self.products if p['name'] == product_name), None)
        if not product:
            return

        self.cart.append({'product_id': product['product_id'], 'name': product['name'], 'quantity': quantity})
        self.update_cart_display()

    def filter_products(self, event=None):
        search_term = self.product_search_var.get().lower()

        filtered_products = [p['name'] for p in self.products if search_term in p['name'].lower()]
        self.product_combobox['values'] = filtered_products
        if filtered_products:
            self.product_var.set(filtered_products[0])
        else:
            self.product_var.set("")

    def update_cart_display(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(item['product_id'], item['name'], item['quantity']))

    def remove_from_cart(self):
        selected_item = self.cart_tree.selection()
        if not selected_item:
            return
        item_id = int(self.cart_tree.item(selected_item[0])['values'][0])
        self.cart = [item for item in self.cart if item['product_id'] != item_id]
        self.update_cart_display()

    def edit_quantity(self):
        selected_item = self.cart_tree.selection()
        if not selected_item:
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

    def on_save(self):
        customer_name = self.customer_var.get()
        if not customer_name:
            messagebox.showerror("Validation Error", "Please select a customer.")
            return
        if not self.cart:
            messagebox.showerror("Validation Error", "Cannot create an empty order.")
            return

        customer = next((c for c in self.customers if c['name'] == customer_name), None)
        self.result = {'customer_id': customer['customer_id'], 'items': self.cart}
        self.destroy()
