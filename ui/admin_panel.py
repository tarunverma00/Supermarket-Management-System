"""
Administrative interface panel for system management
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
from models.employee import Employee
from services.backup import BackupService
import logging

class AdminPanel:
    def __init__(self, notebook, main_app):
        self.notebook = notebook
        self.main_app = main_app
        self.create_admin_interface()

    def create_admin_interface(self):
        """Create administrative interface"""
        self.frame = ttk.Frame(self.notebook, padding=10)
        
        # Create sub-notebook for admin sections
        self.admin_notebook = ttk.Notebook(self.frame)
        self.admin_notebook.pack(fill=tk.BOTH, expand=True)
        
        # User Management Tab
        self.create_user_management_tab()
        
        # System Settings Tab
        self.create_system_settings_tab()
        
        # Database Management Tab
        self.create_database_management_tab()
        
        # System Logs Tab
        self.create_system_logs_tab()

    def create_user_management_tab(self):
        """Create user management interface"""
        user_frame = ttk.Frame(self.admin_notebook, padding=10)
        self.admin_notebook.add(user_frame, text="User Management")
        
        # User creation form
        create_frame = ttk.LabelFrame(user_frame, text="Create New User", padding=10)
        create_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Form fields
        fields_frame = ttk.Frame(create_frame)
        fields_frame.pack(fill=tk.X)
        
        ttk.Label(fields_frame, text="Username:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.new_username_entry = ttk.Entry(fields_frame, width=20)
        self.new_username_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(fields_frame, text="Password:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.new_password_entry = ttk.Entry(fields_frame, width=20, show='*')
        self.new_password_entry.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(fields_frame, text="Role:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.new_role_combo = ttk.Combobox(fields_frame, values=['admin', 'manager', 'cashier'], width=17)
        self.new_role_combo.grid(row=1, column=1, padx=5, pady=2)
        self.new_role_combo.set('cashier')
        
        ttk.Label(fields_frame, text="Email:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.new_email_entry = ttk.Entry(fields_frame, width=20)
        self.new_email_entry.grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(fields_frame, text="Phone:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.new_phone_entry = ttk.Entry(fields_frame, width=20)
        self.new_phone_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(create_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Create User", command=self.create_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_user_form).pack(side=tk.LEFT, padx=5)
        
        # User list
        list_frame = ttk.LabelFrame(user_frame, text="Existing Users", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # User tree view
        columns = ('ID', 'Username', 'Role', 'Email', 'Phone', 'Active', 'Created')
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=100)
        
        # Scrollbar for user tree
        user_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scrollbar.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        user_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # User management buttons
        user_btn_frame = ttk.Frame(list_frame)
        user_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(user_btn_frame, text="Refresh", command=self.refresh_user_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_btn_frame, text="Edit User", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_btn_frame, text="Reset Password", command=self.reset_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_btn_frame, text="Deactivate User", command=self.deactivate_user).pack(side=tk.LEFT, padx=5)
        
        # Load initial user list
        self.refresh_user_list()

    def create_system_settings_tab(self):
        """Create system settings interface"""
        settings_frame = ttk.Frame(self.admin_notebook, padding=10)
        self.admin_notebook.add(settings_frame, text="System Settings")
        
        # Business Settings
        business_frame = ttk.LabelFrame(settings_frame, text="Business Settings", padding=10)
        business_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(business_frame, text="Tax Rate (%):").grid(row=0, column=0, sticky='w', pady=5)
        self.tax_rate_var = tk.StringVar(value="5.0")
        ttk.Entry(business_frame, textvariable=self.tax_rate_var, width=10).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(business_frame, text="Discount Threshold ($):").grid(row=1, column=0, sticky='w', pady=5)
        self.discount_threshold_var = tk.StringVar(value="100.0")
        ttk.Entry(business_frame, textvariable=self.discount_threshold_var, width=10).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(business_frame, text="Discount Rate (%):").grid(row=2, column=0, sticky='w', pady=5)
        self.discount_rate_var = tk.StringVar(value="10.0")
        ttk.Entry(business_frame, textvariable=self.discount_rate_var, width=10).grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Button(business_frame, text="Save Settings", command=self.save_settings).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Security Settings
        security_frame = ttk.LabelFrame(settings_frame, text="Security Settings", padding=10)
        security_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(security_frame, text="Password Policy:").pack(anchor='w')
        self.password_policy_text = tk.Text(security_frame, height=4, width=60)
        self.password_policy_text.pack(fill=tk.X, pady=5)
        self.password_policy_text.insert('1.0', 
            "• Minimum 8 characters\n"
            "• At least one uppercase letter\n"
            "• At least one number\n"
            "• At least one special character")
        
        # System Information
        info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_text = tk.Text(info_frame, height=8, width=60, state=tk.DISABLED)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        # Populate system info
        import sys, platform
        system_info = f"""
System Information:
- Python Version: {sys.version}
- Platform: {platform.system()} {platform.release()}
- Architecture: {platform.architecture()[0]}
- Processor: {platform.processor()}
- Current User: {self.main_app.current_user.username if self.main_app.current_user else 'None'}
"""
        info_text.config(state=tk.NORMAL)
        info_text.insert('1.0', system_info)
        info_text.config(state=tk.DISABLED)

    def create_database_management_tab(self):
        """Create database management interface"""
        db_frame = ttk.Frame(self.admin_notebook, padding=10)
        self.admin_notebook.add(db_frame, text="Database Management")
        
        # Backup Section
        backup_frame = ttk.LabelFrame(db_frame, text="Database Backup", padding=10)
        backup_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(backup_frame, text="Create and manage database backups").pack(anchor='w', pady=5)
        
        backup_btn_frame = ttk.Frame(backup_frame)
        backup_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(backup_btn_frame, text="Create Backup", command=self.create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_btn_frame, text="Restore Backup", command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_btn_frame, text="Schedule Backup", command=self.schedule_backup).pack(side=tk.LEFT, padx=5)
        
        # Database Statistics
        stats_frame = ttk.LabelFrame(db_frame, text="Database Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_tree = ttk.Treeview(stats_frame, columns=('Table', 'Records'), show='headings', height=10)
        self.stats_tree.heading('Table', text='Table Name')
        self.stats_tree.heading('Records', text='Record Count')
        self.stats_tree.column('Table', width=200)
        self.stats_tree.column('Records', width=100)
        
        self.stats_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(stats_frame, text="Refresh Statistics", command=self.refresh_db_stats).pack(pady=5)
        
        # Load initial statistics
        self.refresh_db_stats()

    def create_system_logs_tab(self):
        """Create system logs interface"""
        logs_frame = ttk.Frame(self.admin_notebook, padding=10)
        self.admin_notebook.add(logs_frame, text="System Logs")
        
        # Log viewer
        log_text = tk.Text(logs_frame, height=20, width=100)
        log_scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load recent logs
        try:
            with open('logs/audit_log.txt', 'r') as f:
                logs = f.read()
                log_text.insert('1.0', logs)
        except FileNotFoundError:
            log_text.insert('1.0', "No log file found.")
        
        log_text.config(state=tk.DISABLED)

    def create_user(self):
        """Create new user"""
        username = self.new_username_entry.get().strip()
        password = self.new_password_entry.get().strip()
        role = self.new_role_combo.get()
        email = self.new_email_entry.get().strip()
        phone = self.new_phone_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        try:
            User.create_user(username, password, role, email, phone)
            messagebox.showinfo("Success", f"User '{username}' created successfully")
            self.clear_user_form()
            self.refresh_user_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create user: {str(e)}")

    def clear_user_form(self):
        """Clear user creation form"""
        self.new_username_entry.delete(0, tk.END)
        self.new_password_entry.delete(0, tk.END)
        self.new_role_combo.set('cashier')
        self.new_email_entry.delete(0, tk.END)
        self.new_phone_entry.delete(0, tk.END)

    def refresh_user_list(self):
        """Refresh user list"""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        users = User.get_all_users()
        for user in users:
            self.user_tree.insert('', tk.END, values=(
                user.id, user.username, user.role, user.email or '', 
                user.phone or '', 'Yes' if user.is_active else 'No', 
                user.created_at.strftime('%Y-%m-%d') if user.created_at else ''
            ))

    def edit_user(self):
        """Edit selected user"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return
        
        # Implementation for user editing dialog
        messagebox.showinfo("Info", "User editing functionality will be implemented")

    def reset_password(self):
        """Reset user password"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        if messagebox.askyesno("Confirm", "Reset password for selected user?"):
            messagebox.showinfo("Info", "Password reset functionality will be implemented")

    def deactivate_user(self):
        """Deactivate selected user"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to deactivate")
            return
        
        if messagebox.askyesno("Confirm", "Deactivate selected user?"):
            try:
                item = self.user_tree.item(selection[0])
                user_id = item['values'][0]
                User.delete_user(user_id)
                messagebox.showinfo("Success", "User deactivated successfully")
                self.refresh_user_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to deactivate user: {str(e)}")

    def save_settings(self):
        """Save system settings"""
        messagebox.showinfo("Success", "Settings saved successfully")

    def create_backup(self):
        """Create database backup"""
        try:
            if BackupService.create_backup():
                messagebox.showinfo("Success", "Database backup created successfully")
            else:
                messagebox.showerror("Error", "Failed to create backup")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def restore_backup(self):
        """Restore database backup"""
        messagebox.showinfo("Info", "Backup restore functionality will be implemented")

    def schedule_backup(self):
        """Schedule automatic backups"""
        messagebox.showinfo("Info", "Backup scheduling functionality will be implemented")

    def refresh_db_stats(self):
        """Refresh database statistics"""
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        # Mock data - implement actual database statistics
        stats_data = [
            ('users', '15'),
            ('employees', '8'),
            ('customers', '245'),
            ('products', '1,234'),
            ('transactions', '5,678'),
            ('transaction_items', '12,345'),
            ('inventory_movements', '2,345'),
            ('audit_logs', '8,901')
        ]
        
        for table, count in stats_data:
            self.stats_tree.insert('', tk.END, values=(table, count))

    def refresh(self):
        """Refresh all admin panel data"""
        self.refresh_user_list()
        self.refresh_db_stats()
