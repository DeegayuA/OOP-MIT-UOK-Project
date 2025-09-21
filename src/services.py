"""
Service Layer: Contains the business logic of the application.
Coordinates tasks between the GUI and the Data Access Layer.
"""
from database import get_db_connection, _hash_password

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
