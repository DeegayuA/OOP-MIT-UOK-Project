import tkinter as tk
from tkinter import ttk

class HelpWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Help - Keyboard Shortcuts")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        title_label = ttk.Label(main_frame, text="Keyboard Shortcuts", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        shortcuts = {
            "Navigation": {
                "Ctrl+I": "Open Inventory",
                "Ctrl+S": "Open Sales",
                "Ctrl+O": "Open Orders",
                "Ctrl+L": "Logout",
                "Ctrl+H": "Show Help"
            },
            "General": {
                "Ctrl+N": "Create New Item (in active view)",
                "Ctrl+F": "Search/Filter",
                "F5": "Refresh View"
            },
            "Forms": {
                "Enter": "Submit Form",
                "Esc": "Cancel / Close Window"
            }
        }

        for category, scs in shortcuts.items():
            category_frame = ttk.LabelFrame(main_frame, text=category, padding=(10, 5))
            category_frame.pack(fill='x', expand=True, pady=5)

            for i, (key, desc) in enumerate(scs.items()):
                key_label = ttk.Label(category_frame, text=key, font=("Arial", 10, "bold"))
                key_label.grid(row=i, column=0, padx=5, pady=2, sticky='w')

                desc_label = ttk.Label(category_frame, text=desc)
                desc_label.grid(row=i, column=1, padx=5, pady=2, sticky='w')

        close_button = ttk.Button(main_frame, text="Close", command=self.destroy)
        close_button.pack(pady=20)
