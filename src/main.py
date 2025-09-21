import tkinter as tk
from database import initialize_database

def main():
    """Main function to run the application."""
    # Initialize the database first
    initialize_database()

    # For now, we just show a message.
    # In the future, this will launch the login window.
    root = tk.Tk()
    root.title("Inventory and Sales Management System")
    label = tk.Label(root, text="Application Initialized. Database is ready.", padx=20, pady=20)
    label.pack()
    root.mainloop()

if __name__ == "__main__":
    main()
