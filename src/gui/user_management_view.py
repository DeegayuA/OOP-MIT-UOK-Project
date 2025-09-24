import tkinter as tk
from tkinter import ttk, messagebox
from services import get_all_users, create_user, update_user, delete_user, get_user_by_id

class UserManagementView(ttk.Frame):
    def __init__(self, parent, user_info, app_controller):
        super().__init__(parent)
        self.user_info = user_info
        self.app_controller = app_controller
        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        # Top frame for navigation
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill='x', side='top')
        back_button = ttk.Button(top_frame, text="< Back to Dashboard", command=self.back_to_dashboard)
        back_button.pack(side='left')
        ttk.Label(top_frame, text="User Management", font=("Arial", 16)).pack(side='left', padx=20)

        # Frame for the Treeview and Scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Treeview to display users
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Username', 'Role', 'Active'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Role', text='Role')
        self.tree.heading('Active', text='Active')

        self.tree.column('ID', width=50)
        self.tree.column('Username', width=150)
        self.tree.column('Role', width=100)
        self.tree.column('Active', width=80)

        self.tree.pack(side='left', expand=True, fill='both')

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Frame for buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))

        # Buttons
        add_button = ttk.Button(button_frame, text="Add User", command=self.add_user_dialog)
        add_button.pack(side='left', padx=5)

        edit_button = ttk.Button(button_frame, text="Edit User", command=self.edit_user_dialog)
        edit_button.pack(side='left', padx=5)

        delete_button = ttk.Button(button_frame, text="Delete User", command=self.delete_user)
        delete_button.pack(side='left', padx=5)

    def back_to_dashboard(self):
        self.app_controller.show_main_dashboard()

    def load_users(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load users from the database
        users = get_all_users()
        for user in users:
            self.tree.insert('', 'end', values=(user['user_id'], user['username'], user['role'], 'Yes' if user['is_active'] else 'No'))

    def add_user_dialog(self):
        # Dialog for adding a new user
        dialog = UserDialog(self, title="Add User")
        self.wait_window(dialog)
        if dialog.result:
            username, password, role = dialog.result
            try:
                create_user(username, password, role)
                self.load_users()
                messagebox.showinfo("Success", "User created successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user: {e}")

    def edit_user_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to edit.")
            return

        user_id = self.tree.item(selected_item)['values'][0]
        dialog = UserDialog(self, title="Edit User", user_id=user_id)
        self.wait_window(dialog)
        if dialog.result:
            username, password, role, is_active = dialog.result
            try:
                update_user(user_id, username, password, role, is_active)
                self.load_users()
                messagebox.showinfo("Success", "User updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user: {e}")

    def delete_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to delete.")
            return

        user_id = self.tree.item(selected_item)['values'][0]

        if user_id == self.user_info['user_id']:
            messagebox.showerror("Error", "You cannot delete your own account.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
            try:
                delete_user(user_id)
                self.load_users()
                messagebox.showinfo("Success", "User deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")

class UserDialog(tk.Toplevel):
    def __init__(self, parent, title, user_id=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.user_id = user_id

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.role = tk.StringVar(value='Viewer') # Default role
        self.is_active = tk.BooleanVar(value=True)

        self.create_widgets()

        if self.user_id:
            user_data = get_user_by_id(self.user_id)
            if user_data:
                self.username.set(user_data['username'])
                self.role.set(user_data['role'])
                self.is_active.set(user_data['is_active'])

    def create_widgets(self):
        self.bind('<Escape>', lambda e: self.destroy())

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(expand=True, fill="both")

        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        username_entry = ttk.Entry(form_frame, textvariable=self.username)
        username_entry.grid(row=0, column=1, sticky="ew")
        username_entry.bind("<Return>", lambda e: self.on_ok())


        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        password_entry = ttk.Entry(form_frame, textvariable=self.password, show="*")
        password_entry.grid(row=1, column=1, sticky="ew")
        password_entry.bind("<Return>", lambda e: self.on_ok())

        ttk.Label(form_frame, text="Role:").grid(row=2, column=0, sticky="w", pady=5)
        role_menu = ttk.Combobox(form_frame, textvariable=self.role, values=['Viewer', 'Seller', 'Manager', 'Admin'])
        role_menu.grid(row=2, column=1, sticky="ew")
        role_menu.bind("<Return>", lambda e: self.on_ok())

        if self.user_id:
            ttk.Checkbutton(form_frame, text="Active", variable=self.is_active).grid(row=3, columnspan=2, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)

        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.pack(side="right", padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="right")

    def on_ok(self):
        if self.user_id:
            self.result = (self.username.get(), self.password.get(), self.role.get(), self.is_active.get())
        else:
            self.result = (self.username.get(), self.password.get(), self.role.get())
        self.destroy()
