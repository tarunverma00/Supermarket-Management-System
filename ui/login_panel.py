"""
User login interface panel

"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
import logging

class LoginPanel:
    def __init__(self, notebook, main_app):
        self.notebook = notebook
        self.main_app = main_app
        self.create_login_interface()

    def create_login_interface(self):
        """Create login form interface"""
        self.frame = ttk.Frame(self.notebook, padding=20)
        
        # Main container with centering
        main_container = ttk.Frame(self.frame)
        main_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Logo/Title
        title_label = ttk.Label(main_container, text="SUPERMARKET MANAGEMENT SYSTEM", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        subtitle_label = ttk.Label(main_container, text="Please login to continue", 
                                  style='Heading.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Login form
        login_frame = ttk.LabelFrame(main_container, text="Login Credentials", padding=20)
        login_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky='ew')
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(login_frame, font=('Segoe UI', 12), width=20)
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.username_entry.focus()
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(login_frame, font=('Segoe UI', 12), width=20, show='*')
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(login_frame, text="Remember me", variable=self.remember_var)
        remember_check.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Login button
        login_button = ttk.Button(login_frame, text="LOGIN", command=self.attempt_login,
                                 style='Custom.TButton')
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Status message
        self.status_label = ttk.Label(login_frame, text="", foreground='red')
        self.status_label.grid(row=4, column=0, columnspan=2)
        
        # Bind Enter key to login
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.attempt_login())
        
        # Default credentials hint
        hint_frame = ttk.Frame(main_container)
        hint_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Label(hint_frame, text="Default Login:", font=('Segoe UI', 9, 'italic')).pack()
        ttk.Label(hint_frame, text="Username: admin", font=('Segoe UI', 9, 'italic')).pack()
        ttk.Label(hint_frame, text="Password: admin", font=('Segoe UI', 9, 'italic')).pack()

    def attempt_login(self):
        """Attempt to authenticate user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.show_status("Please enter both username and password", 'red')
            return
        
        # Show loading status
        self.show_status("Authenticating...", 'blue')
        self.frame.update()
        
        try:
            # Authenticate user
            user, message = User.authenticate(username, password)
            
            if user:
                self.show_status("Login successful!", 'green')
                self.clear_form()
                self.main_app.login_successful(user)
            else:
                self.show_status(f"Login failed: {message}", 'red')
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            self.show_status("Login error occurred. Please try again.", 'red')

    def show_status(self, message, color='red'):
        """Show status message"""
        self.status_label.config(text=message, foreground=color)

    def clear_form(self):
        """Clear login form"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.status_label.config(text="")
