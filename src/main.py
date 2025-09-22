import tkinter as tk
from tkinter import ttk
from database import initialize_database
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from gui.inventory_view import InventoryView
from gui.sales_view import SalesView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory and Sales Management System")
        self.withdraw()  # Hide the root window initially

        self.current_user = None
        self.current_frame = None

        self.show_loading_screen()

    def show_loading_screen(self):
        self.loading_win = tk.Toplevel(self)
        self.loading_win.title("Loading...")
        self.loading_win.geometry("200x100")

        # Center the loading window
        self.loading_win.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.loading_win.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.loading_win.winfo_height() // 2)
        self.loading_win.geometry(f"+{x}+{y}")

        ttk.Label(self.loading_win, text="Loading Application...", font=("Arial", 12)).pack(expand=True)

        # Schedule the login window to appear after 2 seconds
        self.after(2000, self.show_login_window)

    def show_login_window(self):
        # Destroy the loading screen if it exists
        if hasattr(self, 'loading_win'):
            self.loading_win.destroy()

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

    def show_sales_view(self):
        """Shows the sales view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = SalesView(self, app_controller=self)
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
