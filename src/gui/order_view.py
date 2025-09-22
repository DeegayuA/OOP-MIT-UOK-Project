import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import services
from gui.base_window import BaseWindow

class OrderView(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Label(main_frame, text="Customer Orders", font=("Arial", 16)).pack(pady=5)
        self.orders_tree = ttk.Treeview(main_frame, columns=("id", "customer", "date", "status"), show="headings")
        self.orders_tree.heading("id", text="Order ID"); self.orders_tree.heading("customer", text="Customer Name"); self.orders_tree.heading("date", text="Order Date"); self.orders_tree.heading("status", text="Status")
        self.orders_tree.column("id", width=80)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(button_frame, text="Create New Order", command=self.create_new_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Status", command=self.update_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back to Dashboard", command=self.app_controller.show_main_dashboard).pack(side=tk.RIGHT, padx=5)

    def refresh_data(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        orders = services.get_all_orders_with_customer_names()
        for o in orders:
            # Handle case where customer might be deleted
            customer_name = o['customer_name'] if o['customer_name'] else "N/A"
            self.orders_tree.insert("", tk.END, values=(o['order_id'], customer_name, o['order_date'], o['status']))

    def update_status(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an order to update.")
            return

        order_id = self.orders_tree.item(selected_item[0])['values'][0]
        current_status = self.orders_tree.item(selected_item[0])['values'][3]

        statuses = ['Received', 'Ready to Pack', 'Ready to Distribute', 'Completed']
        new_status = simpledialog.askstring("Update Status", "Enter new status:", initialvalue=current_status, parent=self)

        if new_status and new_status in statuses:
            try:
                services.update_order_status(order_id, new_status)
                messagebox.showinfo("Success", "Order status updated successfully.")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status: {e}")
        elif new_status:
            messagebox.showerror("Validation Error", f"Invalid status. Must be one of: {', '.join(statuses)}")

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

        # Product selection and cart
        product_frame = ttk.LabelFrame(middle_frame, text="Add Products")
        product_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        cart_frame = ttk.LabelFrame(middle_frame, text="Order Items")
        cart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(product_frame, text="Product:").pack()
        self.product_var = tk.StringVar()
        product_names = [p['name'] for p in self.products]
        ttk.Combobox(product_frame, textvariable=self.product_var, values=product_names, state="readonly").pack(pady=5)

        ttk.Label(product_frame, text="Quantity:").pack()
        self.quantity_var = tk.IntVar(value=1)
        ttk.Spinbox(product_frame, from_=1, to=999, textvariable=self.quantity_var).pack(pady=5)
        ttk.Button(product_frame, text="Add to Order", command=self.add_to_cart).pack(pady=10)

        self.cart_tree = ttk.Treeview(cart_frame, columns=("id", "name", "qty"), show="headings")
        self.cart_tree.heading("id", text="ID"); self.cart_tree.heading("name", text="Product"); self.cart_tree.heading("qty", text="Quantity")
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        # Bottom buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Save Order", command=self.on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

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

    def update_cart_display(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(item['product_id'], item['name'], item['quantity']))

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
