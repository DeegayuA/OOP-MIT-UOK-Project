import tkinter as tk
from tkinter import ttk
from services import authenticate_user

class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_success):
        super().__init__(parent, padding="20")
        self.on_success = on_success

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Configure grid to expand widgets
        self.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(self, text="User Login", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Username
        ttk.Label(self, text="Username:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(self, textvariable=self.username, width=30)
        username_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: self.login())

        # Password
        ttk.Label(self, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        password_entry = ttk.Entry(self, textvariable=self.password, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        password_entry.bind("<Return>", lambda event: self.login())

        # Login Button
        login_button = ttk.Button(self, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=(20, 10))

        # Status Message
        self.message_label = ttk.Label(self, text="", foreground="red")
        self.message_label.grid(row=4, column=0, columnspan=2)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            self.message_label.config(text="Username and password are required.")
            return

        user_info = authenticate_user(username, password)

        if user_info:
            # The controller (App) will handle destroying this frame
            self.on_success(user_info)
        else:
            self.message_label.config(text="Invalid username or password.")
            self.password.set("")
