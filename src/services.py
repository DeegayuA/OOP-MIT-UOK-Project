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
