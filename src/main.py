import tkinter as tk
from database import initialize_database
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from gui.inventory_view import InventoryView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory and Sales Management System")
        self.withdraw()  # Hide the root window initially

        self.current_user = None
        self.current_frame = None

        self.show_login_window()

    def show_login_window(self):
        """Hides the main window and shows the login window."""
        # Clear any existing frame
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

        self.withdraw() # Hide main window
        # Keep a reference to the window to prevent it from being garbage collected
        self.login_win = LoginWindow(self, on_success=self.on_login_success)

    def on_login_success(self, user_info):
        """Callback function for when login is successful."""
        self.current_user = user_info
        self.deiconify() # Show the main window
        self.geometry("800x600")
        self.show_main_dashboard()

    def show_main_dashboard(self):
        """Shows the main dashboard view."""
        if self.current_frame:
            self.current_frame.destroy()

        # Pass the App instance itself as the controller
        self.current_frame = MainWindow(self, self.current_user, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_inventory_view(self):
        """Shows the inventory management view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = InventoryView(self, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

def main():
    """Main function to run the application."""
    # Initialize the database first
    initialize_database()

    # Run the application
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
