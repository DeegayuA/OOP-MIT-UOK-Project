"""
Service Layer: Contains the business logic of the application.
Coordinates tasks between the GUI and the Data Access Layer.
"""
from database import get_db_connection, _hash_password
from datetime import date, timedelta

def log_activity(user_id, action_description):
    """Logs an activity for a given user."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO activity_logs (user_id, action_description) VALUES (?, ?)",
            (user_id, action_description)
        )
        conn.commit()
    finally:
        conn.close()

def create_sale(user_id, customer_id, cart):
    """
    Creates a new sale, updating batch quantities transactionally.
    `cart` is a list of dictionaries, e.g., [{'product_id': 1, 'quantity': 2}, ...]
    """
    conn = get_db_connection()
    try:
        total_amount = 0

        # First, calculate total amount and check stock availability
        for item in cart:
            product_id = item['product_id']
            quantity_to_sell = item['quantity']

            batches = get_batches_for_product(product_id)
            if not batches:
                raise ValueError(f"No batches available for product ID {product_id}")

            total_stock = sum(b['quantity'] for b in batches)
            if total_stock < quantity_to_sell:
                raise ValueError(f"Not enough stock for product ID {product_id}. Available: {total_stock}, Requested: {quantity_to_sell}")

            # The price is determined by the first batch we'd sell from
            total_amount += batches[0]['selling_price'] * quantity_to_sell

        # --- Begin Transaction ---
        cursor = conn.cursor()

        # 1. Create the sale record
        cursor.execute(
            "INSERT INTO sales (user_id, customer_id, total_amount) VALUES (?, ?, ?)",
            (user_id, customer_id, total_amount)
        )
        sale_id = cursor.lastrowid

        # 2. Add sale items and update batch quantities
        for item in cart:
            product_id = item['product_id']
            quantity_to_sell = item['quantity']

            # Get batches again, this time for updating (ordered by expiry)
            batches = get_batches_for_product(product_id)

            for batch in batches:
                if quantity_to_sell == 0:
                    break

                sell_from_this_batch = min(quantity_to_sell, batch['quantity'])

                # Insert sale item record
                cursor.execute(
                    "INSERT INTO sale_items (sale_id, batch_id, quantity_sold, price_per_unit) VALUES (?, ?, ?, ?)",
                    (sale_id, batch['batch_id'], sell_from_this_batch, batch['selling_price'])
                )

                # Update batch quantity
                new_quantity = batch['quantity'] - sell_from_this_batch
                cursor.execute(
                    "UPDATE batches SET quantity = ? WHERE batch_id = ?",
                    (new_quantity, batch['batch_id'])
                )

                quantity_to_sell -= sell_from_this_batch

        conn.commit()
        log_activity(user_id, f"Created new sale with ID {sale_id}.")
        return sale_id

    except (sqlite3.Error, ValueError) as e:
        conn.rollback()
        print(f"Sale creation failed. Rolled back transaction. Error: {e}")
        raise e # Re-raise the exception to be caught by the UI layer
    finally:
        conn.close()

# --- Sales Management Services ---

def get_all_customers():
    """Retrieves all customers from the database."""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT customer_id, name, contact_info FROM customers ORDER BY name")
        customers = cursor.fetchall()
        return [dict(row) for row in customers]
    finally:
        conn.close()

def get_products_for_sale():
    """
    Retrieves all products that are available for sale.
    An available product has at least one batch with quantity > 0.
    The price is determined by the batch that will expire first (FIFO/FEFO).
    """
    conn = get_db_connection()
    try:
        # This query finds the earliest-expiring batch with stock for each product
        # and joins it with the product information.
        cursor = conn.execute("""
            SELECT
                p.product_id,
                p.name,
                p.category,
                b.selling_price
            FROM products p
            JOIN (
                SELECT
                    product_id,
                    MIN(expiry_date) as min_expiry_date
                FROM batches
                WHERE quantity > 0
                GROUP BY product_id
            ) as earliest_exp_batch ON p.product_id = earliest_exp_batch.product_id
            JOIN batches b ON p.product_id = b.product_id AND b.expiry_date = earliest_exp_batch.min_expiry_date
            WHERE b.quantity > 0
            ORDER BY p.name
        """)
        products = cursor.fetchall()
        return [dict(row) for row in products]
    finally:
        conn.close()

def authenticate_user(username, password):
    """
    Authenticates a user.

    Args:
        username (str): The username to authenticate.
        password (str): The password to check.

    Returns:
        A dictionary with user info (user_id, username, role) if authentication is successful,
        otherwise None.
    """
    conn = get_db_connection()
    try:
        user_cursor = conn.execute("SELECT user_id, username, password_hash, role, is_active FROM users WHERE username = ?", (username,))
        user_data = user_cursor.fetchone()
    finally:
        conn.close()

    if not user_data:
        return None  # User not found

    if not user_data['is_active']:
        return None # User is not active

    stored_hash = user_data['password_hash']
    provided_hash = _hash_password(password)

    if stored_hash == provided_hash:
        user_info = {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'role': user_data['role']
        }
        # Log the successful login
        log_activity(user_info['user_id'], f"User '{username}' logged in.")
        return user_info

    return None

def get_dashboard_stats():
    """Fetches key statistics for the main dashboard."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # 1. Total Sales Today
        today = date.today().strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT SUM(total_amount) FROM sales WHERE DATE(sale_date) = ?",
            (today,)
        )
        total_sales_today = cursor.fetchone()[0] or 0.0

        # 2. Items Nearing Expiry (in the next 30 days)
        thirty_days_from_now = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT COUNT(*) FROM batches WHERE expiry_date BETWEEN ? AND ? AND quantity > 0",
            (today, thirty_days_from_now)
        )
        near_expiry_items = cursor.fetchone()[0] or 0

        # 3. Low Stock Alerts
        cursor.execute("""
            SELECT COUNT(p.product_id)
            FROM products p
            WHERE (
                SELECT SUM(b.quantity)
                FROM batches b
                WHERE b.product_id = p.product_id
            ) < p.reorder_level
        """)
        low_stock_items = cursor.fetchone()[0] or 0

        return {
            "total_sales_today": total_sales_today,
            "near_expiry_items": near_expiry_items,
            "low_stock_items": low_stock_items
        }
    finally:
        conn.close()

# --- Inventory Management Services ---

def get_all_products():
    """Retrieves all products from the database."""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT product_id, name, category, reorder_level FROM products ORDER BY name")
        products = cursor.fetchall()
        return [dict(row) for row in products]
    finally:
        conn.close()

def get_batches_for_product(product_id):
    """Retrieves all batches for a specific product."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT batch_id, batch_number, quantity, manufacture_date, expiry_date, cost_price, selling_price "
            "FROM batches WHERE product_id = ? ORDER BY expiry_date",
            (product_id,)
        )
        batches = cursor.fetchall()
        return [dict(row) for row in batches]
    finally:
        conn.close()

def add_product(name, category, reorder_level):
    """Adds a new product to the database."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO products (name, category, reorder_level) VALUES (?, ?, ?)",
            (name, category, reorder_level)
        )
        conn.commit()
    finally:
        conn.close()

def update_product(product_id, name, category, reorder_level):
    """Updates an existing product."""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE products SET name = ?, category = ?, reorder_level = ? WHERE product_id = ?",
            (name, category, reorder_level, product_id)
        )
        conn.commit()
    finally:
        conn.close()

def add_batch(product_id, data):
    """Adds a new batch for a product."""
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO batches (product_id, batch_number, quantity, manufacture_date, expiry_date, cost_price, selling_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_id,
                data['batch_number'],
                data['quantity'],
                data['manufacture_date'],
                data['expiry_date'],
                data['cost_price'],
                data['selling_price']
            )
        )
        conn.commit()
    finally:
        conn.close()
