import tkinter as tk
from tkinter import ttk
from services import authenticate_user
from gui.base_window import BaseWindow

class LoginWindow(BaseWindow):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("User Login")
        self.geometry("300x150")
        self.resizable(False, False)

        self.on_success = on_success
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.master.destroy) # Exit app if this window is closed
        self.center_window()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Username
        ttk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(self, textvariable=self.username)
        username_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: self.login())

        # Password
        ttk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        password_entry = ttk.Entry(self, textvariable=self.password, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        password_entry.bind("<Return>", lambda event: self.login())

        # Login Button
        login_button = ttk.Button(self, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Status Message
        self.message_label = ttk.Label(self, text="", foreground="red")
        self.message_label.grid(row=3, column=0, columnspan=2)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            self.message_label.config(text="Username and password are required.")
            return

        user_info = authenticate_user(username, password)

        if user_info:
            self.destroy() # Close the login window
            self.on_success(user_info) # Call the success callback
        else:
            self.message_label.config(text="Invalid username or password.")

if __name__ == "__main__":
    # This is for testing the window independently
    # Note: This test will fail if src is not in the python path
    root = tk.Tk()
    root.withdraw() # Hide the main window

    def on_login_success(user_info):
        print(f"Login successful for user: {user_info['username']}")
        root.destroy()

    app = LoginWindow(root, on_success=on_login_success)
    root.mainloop()
