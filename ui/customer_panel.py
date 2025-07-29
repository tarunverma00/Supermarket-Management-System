"""
Customer relationship management interface
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.customer import Customer
from services.sms_service import SMSService
from services.call_service import CallService
from datetime import datetime
import logging


class CustomerPanel:
    def __init__(self, notebook, main_app):
        self.notebook = notebook
        self.main_app = main_app
        self.create_customer_interface()

    def create_customer_interface(self):
        """Create comprehensive customer management interface"""
        self.frame = ttk.Frame(self.notebook, padding=10)
        
        # Create paned window for layout
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Customer form
        left_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Customer list
        right_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(right_frame, weight=2)
        
        self.create_customer_form(left_frame)
        self.create_customer_list(right_frame)
        self.create_communication_tools(left_frame)
        
        # Load initial data
        self.refresh_customer_list()

    def create_customer_form(self, parent):
        """Create customer input form"""
        form_frame = ttk.LabelFrame(parent, text="Customer Information", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Customer name
        ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky='w', pady=3)
        self.name_entry = ttk.Entry(form_frame, width=25)
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Phone number
        ttk.Label(form_frame, text="Phone Number:").grid(row=1, column=0, sticky='w', pady=3)
        self.phone_entry = ttk.Entry(form_frame, width=25)
        self.phone_entry.grid(row=1, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Email address
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', pady=3)
        self.email_entry = ttk.Entry(form_frame, width=25)
        self.email_entry.grid(row=2, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Address
        ttk.Label(form_frame, text="Address:").grid(row=3, column=0, sticky='w', pady=3)
        self.address_text = tk.Text(form_frame, height=3, width=25)
        self.address_text.grid(row=3, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Date of birth input field
        ttk.Label(form_frame, text="Date of Birth (DD-MM-YYYY):").grid(row=4, column=0, sticky='w', pady=3)
        self.dob_entry = ttk.Entry(form_frame, width=25)
        self.dob_entry.grid(row=4, column=1, sticky='ew', pady=3, padx=(5, 0))
        stats_frame = ttk.LabelFrame(form_frame, text="Customer Statistics", padding=5)
        stats_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.loyalty_points_label = ttk.Label(stats_frame, text="Loyalty Points: 0")
        self.loyalty_points_label.pack(anchor='w')
        

        self.total_purchases_label = ttk.Label(stats_frame, text="Total Purchases: ₹0.00")
        self.total_purchases_label.pack(anchor='w')
        
        self.member_since_label = ttk.Label(stats_frame, text="Member Since: N/A")
        self.member_since_label.pack(anchor='w')
        
        # Action buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Customer", command=self.add_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Update Customer", command=self.update_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete Customer", command=self.delete_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=2)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

    def create_customer_list(self, parent):
        """Create customer list with search functionality"""
        # Search section
        search_frame = ttk.LabelFrame(parent, text="Search Customers", padding=5)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_controls = ttk.Frame(search_frame)
        search_controls.pack(fill=tk.X)
        
        ttk.Label(search_controls, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_controls, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Button(search_controls, text="Search", command=self.search_customers).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_controls, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_controls, text="Refresh", command=self.refresh_customer_list).pack(side=tk.LEFT, padx=2)
        

        list_frame = ttk.LabelFrame(parent, text="Customer Database", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Name', 'Phone', 'Email', 'Loyalty Points', 'Total Purchases', 'Member Since', 'Status')
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.customer_tree.heading(col, text=col)
            if col == 'Name':
                self.customer_tree.column(col, width=120)
            elif col == 'Email':
                self.customer_tree.column(col, width=150)
            elif col == 'Phone':
                self.customer_tree.column(col, width=100)
            elif col == 'Member Since':
                self.customer_tree.column(col, width=100)
            else:
                self.customer_tree.column(col, width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.customer_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.customer_tree.xview)
        self.customer_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        self.customer_tree.bind('<Double-1>', self.on_customer_double_click)

    def create_communication_tools(self, parent):
        """Create SMS and call tools"""
        comm_frame = ttk.LabelFrame(parent, text="Communication Tools", padding=10)
        comm_frame.pack(fill=tk.X, pady=(0, 10))
        
        # SMS section
        sms_frame = ttk.Frame(comm_frame)
        sms_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(sms_frame, text="SMS Message:").pack(anchor='w')
        self.sms_text = tk.Text(sms_frame, height=3, width=30)
        self.sms_text.pack(fill=tk.X, pady=2)
        
        sms_buttons = ttk.Frame(sms_frame)
        sms_buttons.pack(fill=tk.X, pady=2)
        
        ttk.Button(sms_buttons, text="Send SMS", command=self.send_sms).pack(side=tk.LEFT, padx=2)
        ttk.Button(sms_buttons, text="SMS Templates", command=self.show_sms_templates).pack(side=tk.LEFT, padx=2)
        
        # Call section
        call_frame = ttk.Frame(comm_frame)
        call_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(call_frame, text="Call Customer", command=self.call_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(call_frame, text="View Purchase History", command=self.view_purchase_history).pack(side=tk.LEFT, padx=2)

    def add_customer(self):
        """Add new customer"""
        try:
            name = self.name_entry.get().strip()
            phone = self.phone_entry.get().strip()
            email = self.email_entry.get().strip()
            address = self.address_text.get('1.0', tk.END).strip()
            dob = self.dob_entry.get().strip()
            
            if not name or not phone:
                messagebox.showerror("Error", "Name and phone number are required")
                return
            
            # Validate phone number
            if len(phone) < 10:
                messagebox.showerror("Error", "Please enter a valid phone number")
                return
            
            Customer.create_customer(
                name=name,
                phone=phone,
                email=email if email else None,
                address=address if address else None,
                date_of_birth=dob if dob else None
            )
            
            messagebox.showinfo("Success", "Customer added successfully")
            self.clear_form()
            self.refresh_customer_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
            logging.error(f"Error adding customer: {e}")

    def update_customer(self):
        """Update selected customer"""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to update")
            return
        
        try:
            item = self.customer_tree.item(selection[0])
            customer_id = item['values'][0]
            
            name = self.name_entry.get().strip()
            phone = self.phone_entry.get().strip()
            email = self.email_entry.get().strip()
            address = self.address_text.get('1.0', tk.END).strip()
            dob = self.dob_entry.get().strip()
            
            update_data = {}
            if name: update_data['name'] = name
            if phone: update_data['phone'] = phone
            if email: update_data['email'] = email
            if address: update_data['address'] = address
            if dob: update_data['date_of_birth'] = dob
            
            Customer.update_customer(customer_id, **update_data)
            
            messagebox.showinfo("Success", "Customer updated successfully")
            self.refresh_customer_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update customer: {str(e)}")

    def delete_customer(self):
        """Delete selected customer"""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?"):
            return
        
        try:
            item = self.customer_tree.item(selection[0])
            customer_id = item['values'][0]
            customer_name = item['values'][1]
            
            # Use the delete method from Customer model
            Customer.delete_customer(customer_id)
            
            messagebox.showinfo("Success", f"Customer '{customer_name}' deleted successfully")
            self.clear_form()
            self.refresh_customer_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_text.delete('1.0', tk.END)
        self.dob_entry.delete(0, tk.END)
        

        self.loyalty_points_label.config(text="Loyalty Points: 0")
        self.total_purchases_label.config(text="Total Purchases: ₹0.00")
        self.member_since_label.config(text="Member Since: N/A")

    def refresh_customer_list(self):
        """Refresh customer list with real-time data"""
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        try:
            customers = Customer.get_all_customers()
            for customer in customers:
                status = "Active" if customer.is_active else "Inactive"
                
                total_purchases = f"₹{customer.total_purchases:.2f}"
                member_since = customer.get_formatted_member_since() if hasattr(customer, 'get_formatted_member_since') else 'N/A'
                
                # If member_since method doesn't exist, format manually
                if member_since == 'N/A' and hasattr(customer, 'member_since') and customer.member_since:
                    try:
                        if isinstance(customer.member_since, str):
                            date_obj = datetime.strptime(customer.member_since, '%Y-%m-%d').date()
                            member_since = date_obj.strftime('%d-%m-%Y')
                        else:
                            member_since = customer.member_since.strftime('%d-%m-%Y')
                    except:
                        member_since = str(customer.member_since)
                
                self.customer_tree.insert('', tk.END, values=(
                    customer.id,
                    customer.name,
                    customer.phone or '',
                    customer.email or '',
                    customer.loyalty_points,
                    total_purchases,
                    member_since,
                    status
                ))
        except Exception as e:
            logging.error(f"Error refreshing customer list: {e}")
            messagebox.showerror("Error", f"Failed to refresh customer list: {str(e)}")

    def on_search_change(self, event=None):
        """Handle search entry changes - real-time search"""
        search_term = self.search_entry.get().strip()
        if len(search_term) >= 2:  # Start searching after 2 characters
            self.search_customers()
        elif len(search_term) == 0:
            self.refresh_customer_list()

    def search_customers(self):
        """Search customers"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.refresh_customer_list()
            return
        
        try:
            customers = Customer.search_customers(search_term)
            
            # Clear current list
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)
            
            # Populate with search results
            for customer in customers:
                status = "Active" if customer.is_active else "Inactive"
                total_purchases = f"₹{customer.total_purchases:.2f}"
                member_since = customer.get_formatted_member_since() if hasattr(customer, 'get_formatted_member_since') else 'N/A'
                
                self.customer_tree.insert('', tk.END, values=(
                    customer.id,
                    customer.name,
                    customer.phone or '',
                    customer.email or '',
                    customer.loyalty_points,
                    total_purchases,
                    member_since,
                    status
                ))
                
            if not customers:
                # Show no results message
                self.customer_tree.insert('', tk.END, values=(
                    '', 'No customers found', '', '', '', '', '', ''
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def clear_search(self):
        """Clear search and refresh full list"""
        self.search_entry.delete(0, tk.END)
        self.refresh_customer_list()

    def on_customer_select(self, event):
        """Handle customer selection"""
        selection = self.customer_tree.selection()
        if selection:
            item = self.customer_tree.item(selection[0])
            values = item['values']
            
            # Check if it's a valid customer row (not "No customers found")
            if len(values) >= 8 and values[0] != '':
                customer_id = values[0]
                
                # Load customer details into form
                try:
                    customer = Customer.get_customer_by_id(customer_id)
                    if customer:
                        self.load_customer_to_form(customer)
                except Exception as e:
                    logging.error(f"Error loading customer details: {e}")

    def load_customer_to_form(self, customer):
        """Load customer data into form"""
        self.clear_form()
        
        self.name_entry.insert(0, customer.name)
        if customer.phone:
            self.phone_entry.insert(0, customer.phone)
        if customer.email:
            self.email_entry.insert(0, customer.email)
        if customer.address:
            self.address_text.insert('1.0', customer.address)
        if customer.date_of_birth:
            # Convert date format for display
            try:
                if isinstance(customer.date_of_birth, str):
                    date_obj = datetime.strptime(customer.date_of_birth, '%Y-%m-%d').date()
                    display_date = date_obj.strftime('%d-%m-%Y')
                else:
                    display_date = customer.date_of_birth.strftime('%d-%m-%Y')
                self.dob_entry.insert(0, display_date)
            except:
                self.dob_entry.insert(0, str(customer.date_of_birth))
        self.loyalty_points_label.config(text=f"Loyalty Points: {customer.loyalty_points}")
        self.total_purchases_label.config(text=f"Total Purchases: ₹{customer.total_purchases:.2f}")
        
        # Update member since
        member_since = customer.get_formatted_member_since() if hasattr(customer, 'get_formatted_member_since') else 'N/A'
        self.member_since_label.config(text=f"Member Since: {member_since}")

    def on_customer_double_click(self, event):
        """Handle double-click on customer"""
        self.view_purchase_history()

    def send_sms(self):
        """Send SMS to selected customer"""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        item = self.customer_tree.item(selection[0])
        values = item['values']
        
        if len(values) < 3 or values[0] == '':
            messagebox.showwarning("Warning", "Please select a valid customer")
            return
        
        customer_name = values[1]
        customer_phone = values[2]
        
        if not customer_phone:
            messagebox.showwarning("Warning", "Customer has no phone number")
            return
        
        message = self.sms_text.get('1.0', tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message")
            return
        
        try:
            # For demo purposes, show success message
            messagebox.showinfo("SMS Sent", f"SMS sent to {customer_name} ({customer_phone})\n\nMessage: {message}")
            self.sms_text.delete('1.0', tk.END)
            
            # Uncomment below line when SMS service is implemented
            # SMSService.send_sms(customer_phone, message)
        except Exception as e:
            messagebox.showerror("Error", f"SMS sending failed: {str(e)}")

    def show_sms_templates(self):
        """Show SMS templates"""
        templates = [
            "Thank you for shopping with us! Your loyalty is appreciated.",
            "Special offer just for you! Visit our store today for exclusive discounts.",
            "Your order is ready for pickup. Please visit us at your convenience.",
            "Payment reminder: Please settle your account at the earliest.",
            "Happy birthday! Enjoy a special 20% discount on us today.",
            "Your loyalty points are expiring soon. Use them before the end of this month!",
            "New arrivals in store! Be the first to check out our latest collection.",
            "Thank you for your recent purchase. We hope you love your items!"
        ]
        
        template_window = tk.Toplevel(self.frame)
        template_window.title("SMS Templates")
        template_window.geometry("500x400")
        template_window.grab_set()
        
        ttk.Label(template_window, text="Select a template:", font=('Segoe UI', 10, 'bold')).pack(pady=10)
        
        listbox = tk.Listbox(template_window, height=10, font=('Segoe UI', 9))
        for template in templates:
            listbox.insert(tk.END, template)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def use_template():
            selection = listbox.curselection()
            if selection:
                template = listbox.get(selection[0])
                self.sms_text.delete('1.0', tk.END)
                self.sms_text.insert('1.0', template)
                template_window.destroy()
            else:
                messagebox.showwarning("Selection Required", "Please select a template")
        
        button_frame = ttk.Frame(template_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Use Template", command=use_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=template_window.destroy).pack(side=tk.LEFT, padx=5)

    def call_customer(self):
        """Call selected customer"""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        item = self.customer_tree.item(selection[0])
        values = item['values']
        
        if len(values) < 3 or values[0] == '':
            messagebox.showwarning("Warning", "Please select a valid customer")
            return
        
        customer_name = values[1]
        customer_phone = values[2]
        
        if not customer_phone:
            messagebox.showwarning("Warning", "Customer has no phone number")
            return
        
        try:
            # For demo purposes, show call dialog
            result = messagebox.askyesno("Make Call", f"Call {customer_name} at {customer_phone}?")
            if result:
                messagebox.showinfo("Calling", f"Calling {customer_name}...\nPhone: {customer_phone}")
            
            # Uncomment below line when call service is implemented
            # CallService.make_call(customer_phone, f"Hello {customer_name}, this is a call from the supermarket.")
        except Exception as e:
            messagebox.showerror("Error", f"Call failed: {str(e)}")

    def view_purchase_history(self):
        """View customer purchase history with enhanced details"""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        item = self.customer_tree.item(selection[0])
        values = item['values']
        
        if len(values) < 2 or values[0] == '':
            messagebox.showwarning("Warning", "Please select a valid customer")
            return
        
        customer_id = values[0]
        customer_name = values[1]
        
        try:
            history = Customer.get_customer_purchase_history(customer_id)
            
            # Create history window
            history_window = tk.Toplevel(self.frame)
            history_window.title(f"Purchase History - {customer_name}")
            history_window.geometry("900x600")
            history_window.grab_set()
            
            # Header
            header_frame = ttk.Frame(history_window)
            header_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(header_frame, text=f"Purchase History for: {customer_name}", 
                     font=('Segoe UI', 12, 'bold')).pack(anchor='w')
            
            # Create treeview for history
            tree_frame = ttk.Frame(history_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            columns = ('Transaction ID', 'Date', 'Amount', 'Payment Method')
            history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
            
            for col in columns:
                history_tree.heading(col, text=col)
                if col == 'Transaction ID':
                    history_tree.column(col, width=150)
                elif col == 'Date':
                    history_tree.column(col, width=100)
                elif col == 'Amount':
                    history_tree.column(col, width=100, anchor='e')
                else:
                    history_tree.column(col, width=120)
            
            # Add scrollbar
            hist_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=history_tree.yview)
            history_tree.configure(yscrollcommand=hist_scrollbar.set)
            
            history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            hist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            total_spent = 0
            for record in history:
                # Format amount in rupees
                amount = f"₹{record[3]:.2f}"
                # Format date
                date_str = record[2] if isinstance(record[2], str) else record[2].strftime('%d-%m-%Y')
                
                history_tree.insert('', tk.END, values=(record[1], date_str, amount, record[4]))
                total_spent += record[3]
            
            if not history:
                history_tree.insert('', tk.END, values=('No transactions found', '', '', ''))
            summary_frame = ttk.Frame(history_window)
            summary_frame.pack(fill=tk.X, padx=10, pady=10)
            
            summary_text = f"Total Transactions: {len(history)} | Total Spent: ₹{total_spent:.2f}"
            if history:
                avg_purchase = total_spent / len(history)
                summary_text += f" | Average Purchase: ₹{avg_purchase:.2f}"
            
            ttk.Label(summary_frame, text=summary_text, font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            
            # Close button
            ttk.Button(history_window, text="Close", command=history_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load purchase history: {str(e)}")

    def refresh(self):
        """Refresh panel data"""
        self.refresh_customer_list()
