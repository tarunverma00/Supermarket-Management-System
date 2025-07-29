"""
Main application window with tabbed interface

"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from config import WINDOW_TITLE, THEME
from ui.login_panel import LoginPanel
from ui.admin_panel import AdminPanel
from ui.inventory_panel import InventoryPanel
from ui.billing_panel import BillingPanel
from ui.customer_panel import CustomerPanel
from ui.employee_panel import EmployeePanel
from ui.report_panel import ReportPanel
from ui.utils import UIUtils

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.current_user = None
        self.setup_window()
        self.setup_styles()
        self.create_menu()
        self.create_status_bar()
        self.setup_main_interface()
        self.show_login()

    def setup_window(self):
        """Configure main window properties"""
        self.root.title(WINDOW_TITLE)
        self.root.state('zoomed')  # Maximize window on Windows
        self.root.attributes('-fullscreen', True)  # Full screen
        self.root.configure(bg='#f0f0f0')
        
        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)

    def setup_styles(self):
        """Configure UI styles and themes"""
        self.style = ttk.Style()
        self.style.theme_use(THEME)
        
        # Custom styles for professional appearance
        self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Custom.TButton', padding=10, font=('Segoe UI', 10))
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        self.style.configure('Treeview', font=('Segoe UI', 9))
        
        # Color scheme
        self.style.configure('Custom.TFrame', background='#ffffff')
        self.style.configure('Sidebar.TFrame', background='#2c3e50')

    def create_menu(self):
        """Create application menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen)
        view_menu.add_command(label="Refresh", command=self.refresh_all_panels)
        
        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Backup Database", command=self.backup_database)
        tools_menu.add_command(label="System Logs", command=self.view_logs)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)

    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.user_label = ttk.Label(self.status_frame, text="Not logged in", relief=tk.SUNKEN)
        self.user_label.pack(side=tk.RIGHT)
        
        self.time_label = ttk.Label(self.status_frame, text="", relief=tk.SUNKEN)
        self.time_label.pack(side=tk.RIGHT)
        
        self.update_time()

    def setup_main_interface(self):
        """Setup main tabbed interface"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initialize all panels
        self.panels = {}
        self.create_all_panels()

    def create_all_panels(self):
        """Create all application panels"""
        try:
            # Login panel (shown first)
            self.panels['login'] = LoginPanel(self.notebook, self)
            
            # Main application panels (hidden until login)
            self.panels['inventory'] = InventoryPanel(self.notebook, self)
            self.panels['billing'] = BillingPanel(self.notebook, self)
            self.panels['customer'] = CustomerPanel(self.notebook, self)
            self.panels['employee'] = EmployeePanel(self.notebook, self)
            self.panels['report'] = ReportPanel(self.notebook, self)
            self.panels['admin'] = AdminPanel(self.notebook, self)
            
            # Add login tab only initially
            self.notebook.add(self.panels['login'].frame, text="Login")
            
        except Exception as e:
            logging.error(f"Error creating panels: {e}")
            messagebox.showerror("Error", f"Failed to create application panels: {str(e)}")

    def show_login(self):
        """Show login panel and hide others"""
        # Clear all tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Show only login tab
        self.notebook.add(self.panels['login'].frame, text="Login")
        self.update_status("Please log in to continue")

    def login_successful(self, user):
        """Handle successful login"""
        self.current_user = user
        self.setup_user_interface()
        self.update_status(f"Welcome, {user.username}!")
        self.user_label.config(text=f"User: {user.username} ({user.role})")
        
        logging.info(f"User logged in successfully: {user.username}")

    def setup_user_interface(self):
        """Setup interface based on user role"""
        # Clear all tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Add tabs based on user role
        if self.current_user.role in ['admin', 'manager']:
            self.notebook.add(self.panels['inventory'].frame, text="Inventory")
            self.notebook.add(self.panels['billing'].frame, text="Billing")
            self.notebook.add(self.panels['customer'].frame, text="Customers")
            self.notebook.add(self.panels['employee'].frame, text="Employees")
            self.notebook.add(self.panels['report'].frame, text="Reports")
            
            if self.current_user.role == 'admin':
                self.notebook.add(self.panels['admin'].frame, text="Administration")
        
        elif self.current_user.role == 'cashier':
            self.notebook.add(self.panels['billing'].frame, text="Billing")
            self.notebook.add(self.panels['customer'].frame, text="Customers")
            
        # Refresh all panels with current user context
        self.refresh_all_panels()
        
        # Select first tab
        self.notebook.select(0)

    def refresh_all_panels(self):
        """Refresh all panels with current data"""
        for panel_name, panel in self.panels.items():
            if hasattr(panel, 'refresh') and panel_name != 'login':
                try:
                    panel.refresh()
                except Exception as e:
                    logging.error(f"Error refreshing {panel_name} panel: {e}")

    def update_time(self):
        """Update time display in status bar"""
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        logging.info(f"Status: {message}")

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.user_label.config(text="Not logged in")
            self.show_login()
            self.update_status("Logged out successfully")

    def backup_database(self):
        """Backup database"""
        try:
            from services.backup import BackupService
            if BackupService.create_backup():
                messagebox.showinfo("Success", "Database backup created successfully")
            else:
                messagebox.showerror("Error", "Failed to create database backup")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def view_logs(self):
        """Open log viewer"""
        UIUtils.show_log_viewer(self.root)

    def show_help(self):
        """Show help documentation"""
        help_text = """
        SUPERMARKET MANAGEMENT SYSTEM - USER GUIDE
        
        NAVIGATION:
        - Use tabs to navigate between different sections
        - Press F11 or Escape to toggle fullscreen
        - Use Ctrl+R to refresh all data
        
        ROLES AND PERMISSIONS:
        - Admin: Full system access
        - Manager: Inventory, billing, reports, customers, employees
        - Cashier: Billing and customer management only
        
        BILLING:
        - Scan barcodes or search products manually
        - Add items to cart and process payment
        - Print receipts and handle refunds
        
        INVENTORY:
        - Add, edit, and remove products
        - Monitor stock levels and expiry dates
        - Set reorder levels and manage suppliers
        
        CUSTOMERS:
        - Maintain customer database
        - Send SMS and make calls
        - Track loyalty points and purchase history
        
        For technical support, contact your system administrator.
        """
        UIUtils.show_text_dialog(self.root, "User Guide", help_text)

    def show_about(self):
        """Show about dialog"""
        about_text = """
        SUPERMARKET MANAGEMENT SYSTEM
        Version 1.0.0
        
        A comprehensive retail management solution built with Python.
        
        Features:
        • Point of Sale (POS) System
        • Inventory Management
        • Customer Relationship Management
        • Employee Management
        • Advanced Reporting
        • SMS/Call Integration
        
        Copyright (c) 2024 [Your Company Name]
        All rights reserved.
        
        Built with Python, Tkinter, and MySQL.
        """
        UIUtils.show_text_dialog(self.root, "About", about_text)

    def exit_application(self):
        """Exit application with confirmation"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
            logging.info("Application closing...")
            self.root.quit()
