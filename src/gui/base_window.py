import tkinter as tk

class BaseWindow(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        self.grab_set()

    def center_window(self):
        self.update_idletasks()

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Get window width and height
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        # Calculate position
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.geometry(f'{window_width}x{window_height}+{x}+{y}')
