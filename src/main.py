import tkinter as tk
from tkinter import ttk
from database import initialize_database
from ttkthemes import ThemedTk
from gui.login_window import LoginFrame
from gui.main_window import MainWindow
from gui.inventory_view import InventoryView
from gui.sales_view import SalesView
from gui.order_view import OrderView

class App(ThemedTk):
    def __init__(self):
        super().__init__(theme="adapta")  # Set a modern theme
        self.title("Inventory and Sales Management System")
        # Set a min size for the app window
        self.minsize(400, 300)

        self.current_user = None
        self.current_frame = None

        self.show_login_frame()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        self.bind("<Control-n>", lambda event: self.handle_new_item_shortcut())

    def handle_new_item_shortcut(self):
        # This is a bit of a hack, as we don't know which "new" action to take.
        # A more robust solution would be a proper menu bar.
        # For now, we'll check the type of the current frame.
        from gui.inventory_view import InventoryView
        from gui.order_view import OrderView

        if isinstance(self.current_frame, InventoryView):
            # In inventory view, "new" could mean new product or new batch.
            # We'll default to new product.
            self.current_frame.add_product()
        elif isinstance(self.current_frame, OrderView):
            self.current_frame.create_new_order()

    def center_window(self, width, height):
        """Centers the main window on the screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def show_login_frame(self):
        """Shows the login frame in the main window."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("User Login")
        self.center_window(400, 300)
        self.current_frame = LoginFrame(self, on_success=self.on_login_success)
        self.current_frame.pack(expand=True)

    def on_login_success(self, user_info):
        """Callback function for when login is successful."""
        self.current_user = user_info
        self.show_main_dashboard()

    def show_main_dashboard(self):
        """Shows the main dashboard view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("Main Dashboard")
        self.center_window(900, 600)
        self.current_frame = MainWindow(self, self.current_user, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame.update_stats() # Ensure stats are fresh

    def show_inventory_view(self):
        """Shows the inventory management view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("Inventory Management")
        self.current_frame = InventoryView(self, app_controller=self)
        # Check if the view has a frame attribute or is a frame itself
        if hasattr(self.current_frame, 'frame'):
            self.current_frame.frame.pack(fill=tk.BOTH, expand=True)
        elif hasattr(self.current_frame, 'pack_frame'):
            self.current_frame.pack_frame(fill=tk.BOTH, expand=True)
        else:
            # Create a frame and add the view to it
            container = ttk.Frame(self)
            container.pack(fill=tk.BOTH, expand=True)
            self.current_frame.master = container

    def show_sales_view(self):
        """Shows the sales view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("New Sale")
        self.current_frame = SalesView(self, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_order_view(self):
        """Shows the order management view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("Order Management")
        self.current_frame = OrderView(self, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def change_theme(self, theme_name):
        """Changes the application's theme."""
        try:
            self.set_theme(theme_name)
            print(f"Theme changed to {theme_name}")
        except Exception as e:
            print(f"Could not set theme {theme_name}: {e}")

def main():
    """Main function to run the application."""
    initialize_database()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
