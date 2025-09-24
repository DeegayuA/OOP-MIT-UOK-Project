import tkinter as tk
from tkinter import ttk
import time
from database import initialize_database
from ttkthemes import ThemedTk
from gui.login_window import LoginFrame
from gui.main_window import MainWindow
from gui.inventory_view import InventoryView
from gui.sales_view import SalesView
from gui.order_view import OrderView
from gui.help_window import HelpWindow

class App(ThemedTk):
    def __init__(self):
        super().__init__() 
        self.title("Inventory and Sales Management System")
        self.minsize(400, 300)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.current_user = None
        self.current_frame = None

        self.configure_styles()
        self.show_login_frame()
        self.setup_shortcuts()

    def configure_styles(self):
        style = ttk.Style()
        style.configure("Hover.TButton", relief="solid")

    def fade_in_window(self, window):
        window.attributes("-alpha", 0.0)
        window.deiconify()
        start_time = time.time()

        def animate():
            elapsed = time.time() - start_time
            alpha = min(elapsed / 0.2, 1.0) # 200ms fade-in
            window.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.after(10, animate)

        self.after(10, animate)

    def setup_shortcuts(self):
        self.bind("<Control-n>", lambda event: self.handle_new_item_shortcut())
        self.bind("<Control-i>", lambda event: self.show_inventory_view())
        self.bind("<Control-s>", lambda event: self.show_sales_view())
        self.bind("<Control-o>", lambda event: self.show_order_view())
        self.bind("<Control-l>", lambda event: self.show_login_frame())
        self.bind("<Control-h>", lambda event: self.show_help_window())

    def show_help_window(self):
        HelpWindow(self)

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
        self.fade_in_window(self)

    def show_inventory_view(self):
        """Shows the inventory management view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("Inventory Management")
        self.current_frame = InventoryView(self, self.current_user, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.fade_in_window(self)

    def show_sales_view(self):
        """Shows the sales view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("New Sale")
        self.current_frame = SalesView(self, self.current_user, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.fade_in_window(self)

    def show_order_view(self):
        """Shows the order management view."""
        if self.current_frame:
            self.current_frame.destroy()

        self.title("Order Management")
        self.current_frame = OrderView(self, self.current_user, app_controller=self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.fade_in_window(self)

    def change_theme(self, theme_name):
        """Changes the application's theme."""
        try:
            self.set_theme(theme_name)
            print(f"Theme changed to {theme_name}")
        except Exception as e:
            print(f"Could not set theme {theme_name}: {e}")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

def main():
    """Main function to run the application."""
    initialize_database()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
