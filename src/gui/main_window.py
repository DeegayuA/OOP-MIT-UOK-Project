import tkinter as tk
from tkinter import ttk

class MainWindow(tk.Frame):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info

        self.create_widgets()

    def create_widgets(self):
        # Welcome message
        welcome_text = f"Welcome, {self.user_info['username']}! (Role: {self.user_info['role']})"
        welcome_label = ttk.Label(self, text=welcome_text, font=("Arial", 16))
        welcome_label.pack(pady=20)

        # Placeholder for dashboard content
        placeholder_label = ttk.Label(self, text="Main Dashboard - Content will go here.")
        placeholder_label.pack(pady=10)

        # Logout button
        logout_button = ttk.Button(self, text="Logout", command=self.logout)
        logout_button.pack(pady=20)

    def logout(self):
        # This would eventually call a method in the main App to show the login screen again
        print("Logout button clicked.")
        self.parent.destroy()
