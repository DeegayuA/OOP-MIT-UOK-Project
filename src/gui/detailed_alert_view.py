import tkinter as tk
from tkinter import ttk
from .base_window import BaseWindow

class DetailedAlertView(BaseWindow):
    def __init__(self, parent, title, items, columns):
        """
        Initializes a window to display a list of items.
        - parent: The parent window.
        - title: The title of the window.
        - items: A list of dictionaries, where each dict is an item.
        - columns: A dictionary defining the Treeview columns,
                   e.g., {'product_name': 'Product Name', 'quantity': 'Quantity'}
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("700x400")

        self.items = items
        self.columns = columns

        self.create_widgets()
        self.populate_data()
        self.center_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Treeview to display items ---
        column_keys = list(self.columns.keys())
        self.tree = ttk.Treeview(main_frame, columns=column_keys, show="headings")

        for key, heading in self.columns.items():
            self.tree.heading(key, text=heading)
            self.tree.column(key, width=150) # Default width, can be adjusted

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # --- Scrollbar ---
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)

        # --- Close Button ---
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)
        close_button = ttk.Button(button_frame, text="Close", command=self.destroy)
        close_button.pack(side=tk.RIGHT)
        self.bind("<Escape>", lambda e: self.destroy())

    def populate_data(self):
        for item in self.items:
            # Ensure the values are in the same order as the column keys
            values = [item.get(key, "") for key in self.columns.keys()]
            self.tree.insert("", tk.END, values=values)
