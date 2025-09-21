"""
Domain Layer: Contains the core business entities of the application.
"""

class User:
    def __init__(self, user_id, username, password_hash, role, is_active=True):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Product:
    def __init__(self, product_id, name, category, reorder_level):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.reorder_level = reorder_level

    def __repr__(self):
        return f"<Product {self.name}>"

class Batch:
    def __init__(self, batch_id, product_id, batch_number, quantity, manufacture_date, expiry_date, cost_price, selling_price):
        self.batch_id = batch_id
        self.product_id = product_id
        self.batch_number = batch_number
        self.quantity = quantity
        self.manufacture_date = manufacture_date
        self.expiry_date = expiry_date
        self.cost_price = cost_price
        self.selling_price = selling_price

    def __repr__(self):
        return f"<Batch No: {self.batch_number} (Qty: {self.quantity})>"

class Customer:
    def __init__(self, customer_id, name, contact_info):
        self.customer_id = customer_id
        self.name = name
        self.contact_info = contact_info

    def __repr__(self):
        return f"<Customer {self.name}>"

class Sale:
    def __init__(self, sale_id, user_id, customer_id, sale_date, total_amount, discount_applied=0):
        self.sale_id = sale_id
        self.user_id = user_id
        self.customer_id = customer_id
        self.sale_date = sale_date
        self.total_amount = total_amount
        self.discount_applied = discount_applied

class SaleItem:
    def __init__(self, sale_item_id, sale_id, batch_id, quantity_sold, price_per_unit):
        self.sale_item_id = sale_item_id
        self.sale_id = sale_id
        self.batch_id = batch_id
        self.quantity_sold = quantity_sold
        self.price_per_unit = price_per_unit

class Order:
    def __init__(self, order_id, customer_id, order_date, status):
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.status = status

class OrderItem:
    def __init__(self, order_item_id, order_id, product_id, quantity_ordered):
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity_ordered = quantity_ordered

class ActivityLog:
    def __init__(self, log_id, user_id, timestamp, action_description):
        self.log_id = log_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.action_description = action_description
