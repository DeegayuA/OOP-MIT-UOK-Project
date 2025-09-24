from sqlcipher3 import dbapi2 as sqlite3
import hashlib
import bcrypt
import os

# Build a path to the database file in the project's root directory
# This makes the path independent of where the script is run from.
# __file__ is the path to the current script (database.py)
# os.path.dirname(__file__) is the directory of the script (src/)
# os.path.abspath(...) gets the absolute path
# os.path.join(..., '..') goes up one level to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE = os.path.join(PROJECT_ROOT, "inventory.db")
KEY_FILE = os.path.join(PROJECT_ROOT, "db.key")

def get_or_create_db_key():
    """
    Reads the database key from KEY_FILE or generates a new one.
    Returns the key as a hex string.
    """
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as f:
            return f.read().strip()
    else:
        new_key = os.urandom(32).hex()
        with open(KEY_FILE, 'w') as f:
            f.write(new_key)
        return new_key

DB_KEY = get_or_create_db_key()

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"PRAGMA key = '{DB_KEY}'")
        # Test the connection to see if the key is correct
        conn.execute("SELECT count(*) FROM sqlite_master;")
    except sqlite3.DatabaseError:
        # This can happen if the key is wrong or the db is corrupt.
        # As per the user's request, we delete the db and re-initialize.
        conn.close()
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

        # Create a new connection for initialization
        init_conn = sqlite3.connect(DB_FILE)
        init_conn.execute(f"PRAGMA key = '{DB_KEY}'")
        initialize_database(init_conn)

        # Now, the main connection should work
        conn = sqlite3.connect(DB_FILE)
        conn.execute(f"PRAGMA key = '{DB_KEY}'")

    conn.row_factory = sqlite3.Row
    return conn

def _hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def _verify_password(plain_password, hashed_password):
    """Verifies a password against a hashed version."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def delete_product(product_id):
    """Deletes a product from the database."""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        conn.commit()
    finally:
        conn.close()

def delete_batch(batch_id):
    """Deletes a batch from the database."""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM batches WHERE batch_id = ?", (batch_id,))
        conn.commit()
    finally:
        conn.close()

def initialize_database(conn=None):
    """
    Initializes the database and creates tables if they don't exist.
    If a connection object is provided, it uses it. Otherwise, it creates a new one.
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    cursor = conn.cursor()

    # User Management
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'Staff')),
        is_active BOOLEAN NOT NULL DEFAULT 1
    )""")

    # Inventory Management
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL CHECK(category IN ('Water', 'Soft Drink', 'Juice', 'Snack')),
        reorder_level INTEGER NOT NULL DEFAULT 10
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batches (
        batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        batch_number TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        manufacture_date DATE,
        expiry_date DATE,
        cost_price REAL NOT NULL,
        selling_price REAL NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
    )""")

    # Customer Management
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_info TEXT
    )""")

    # Sales Management
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        customer_id INTEGER,
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL NOT NULL,
        discount_applied REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        batch_id INTEGER NOT NULL,
        quantity_sold INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales (sale_id),
        FOREIGN KEY (batch_id) REFERENCES batches (batch_id)
    )""")

    # Order Management
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Received', 'Ready to Pack', 'Ready to Distribute', 'Completed')),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity_ordered INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )""")

    # Activity Logging
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        action_description TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )""")

    # Pre-populate with a default admin user for initial login
    try:
        admin_password = "admin"
        hashed_password = _hash_password(admin_password)
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ('admin', hashed_password, 'Admin'))
    except sqlite3.IntegrityError:
        # Admin user already exists, update password to new hash
        admin_password = "admin"
        hashed_password = _hash_password(admin_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_password, 'admin'))

    conn.commit()
    if close_conn:
        conn.close()
    print("Database initialized successfully.")
