"""
Comprehensive inventory management interface
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from models.product import Product
from models.supplier import Supplier
from datetime import datetime, timedelta
import csv
import logging

class InventoryPanel:
    def __init__(self, notebook, main_app):
        self.notebook = notebook
        self.main_app = main_app
        self.create_inventory_interface()

    def create_inventory_interface(self):
        """Create comprehensive inventory management interface"""
        self.frame = ttk.Frame(self.notebook, padding=10)
        
        # Create main paned window for layout
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Product form and controls
        left_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Product list and details
        right_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(right_frame, weight=2)
        
        self.create_product_form(left_frame)
        self.create_product_list(right_frame)
        self.create_action_buttons(left_frame)
        self.create_alerts_section(left_frame)
        
        # Load initial data
        self.refresh_product_list()
        self.check_alerts()

    def create_product_form(self, parent):
        """Create product input form with proper category handling"""
        form_frame = ttk.LabelFrame(parent, text="Product Information", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Barcode
        ttk.Label(form_frame, text="Barcode:").grid(row=0, column=0, sticky='w', pady=2)
        self.barcode_entry = ttk.Entry(form_frame, width=25)
        self.barcode_entry.grid(row=0, column=1, sticky='ew', pady=2, padx=(5, 0))
        
        ttk.Button(form_frame, text="Scan", command=self.scan_barcode).grid(row=0, column=2, padx=(5, 0))
        
        # Product name
        ttk.Label(form_frame, text="Product Name:").grid(row=1, column=0, sticky='w', pady=2)
        self.name_entry = ttk.Entry(form_frame, width=25)
        self.name_entry.grid(row=1, column=1, columnspan=2, sticky='ew', pady=2, padx=(5, 0))
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky='w', pady=2)
        self.description_entry = tk.Text(form_frame, height=3, width=25)
        self.description_entry.grid(row=2, column=1, columnspan=2, sticky='ew', pady=2, padx=(5, 0))
        
        # Category with proper values and readonly state
        ttk.Label(form_frame, text="Category:").grid(row=3, column=0, sticky='w', pady=2)
        self.category_combo = ttk.Combobox(form_frame, values=self.get_categories(), 
                                         width=22, state="readonly")
        self.category_combo.grid(row=3, column=1, columnspan=2, sticky='ew', pady=2, padx=(5, 0))
        self.category_combo.current(0)  # Set default selection
        
        # Brand
        ttk.Label(form_frame, text="Brand:").grid(row=4, column=0, sticky='w', pady=2)
        self.brand_entry = ttk.Entry(form_frame, width=25)
        self.brand_entry.grid(row=4, column=1, columnspan=2, sticky='ew', pady=2, padx=(5, 0))
        
        # Pricing
        pricing_frame = ttk.Frame(form_frame)
        pricing_frame.grid(row=5, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(pricing_frame, text="Cost Price (₹):").grid(row=0, column=0, sticky='w')
        self.cost_price_entry = ttk.Entry(pricing_frame, width=10)
        self.cost_price_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(pricing_frame, text="Selling Price (₹):").grid(row=0, column=2, sticky='w')
        self.unit_price_entry = ttk.Entry(pricing_frame, width=10)
        self.unit_price_entry.grid(row=0, column=3, padx=5)
        
        # Stock information
        stock_frame = ttk.Frame(form_frame)
        stock_frame.grid(row=6, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(stock_frame, text="Quantity:").grid(row=0, column=0, sticky='w')
        self.quantity_entry = ttk.Entry(stock_frame, width=10)
        self.quantity_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(stock_frame, text="Reorder Level:").grid(row=0, column=2, sticky='w')
        self.reorder_level_entry = ttk.Entry(stock_frame, width=10)
        self.reorder_level_entry.grid(row=0, column=3, padx=5)
        
        # Expiry date with proper positioning
        ttk.Label(form_frame, text="Expiry Date (DD-MM-YYYY):").grid(row=7, column=0, sticky='w', pady=2)
        self.expiry_entry = ttk.Entry(form_frame, width=25)
        self.expiry_entry.grid(row=7, column=1, columnspan=2, sticky='ew', pady=2, padx=(5, 0))
        
        # Supplier section - WORKING VERSION
        ttk.Label(form_frame, text="Supplier:").grid(row=8, column=0, sticky='w', pady=2)

        # Create supplier frame
        supplier_frame = ttk.Frame(form_frame)
        supplier_frame.grid(row=8, column=1, columnspan=2, sticky='ew', pady=2, padx=(5, 0))

        # Create the combobox
        self.supplier_combo = ttk.Combobox(supplier_frame, width=18, state="readonly")
        self.supplier_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Refresh button
        refresh_btn = ttk.Button(supplier_frame, text="↻", width=3, command=self._refresh_suppliers_now)
        refresh_btn.pack(side=tk.LEFT, padx=(2, 0))

        # Add supplier button
        add_btn = ttk.Button(supplier_frame, text="+ Add", width=6, command=self._add_supplier_now)
        add_btn.pack(side=tk.LEFT, padx=(2, 0))

        # Load initial suppliers
        self._refresh_suppliers_now()
        
        # Tax and discount rates
        rates_frame = ttk.Frame(form_frame)
        rates_frame.grid(row=9, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(rates_frame, text="Tax Rate (%):").grid(row=0, column=0, sticky='w')
        self.tax_rate_entry = ttk.Entry(rates_frame, width=8)
        self.tax_rate_entry.grid(row=0, column=1, padx=5)
        self.tax_rate_entry.insert(0, "18.0")  # Default GST rate for India
        
        ttk.Label(rates_frame, text="Discount (%):").grid(row=0, column=2, sticky='w')
        self.discount_rate_entry = ttk.Entry(rates_frame, width=8)
        self.discount_rate_entry.grid(row=0, column=3, padx=5)
        self.discount_rate_entry.insert(0, "0.0")
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

    def _refresh_suppliers_now(self):
        """Force refresh suppliers immediately using direct database queries"""
        try:
            # Use the simple method that directly queries the database
            raw_suppliers = Supplier.get_suppliers_simple()
            
            # Format for display
            supplier_list = [f"{s[0]} - {s[1]}" for s in raw_suppliers]
            
            # Clear and set values
            current_selection = self.supplier_combo.get()
            self.supplier_combo['values'] = ()  # Clear first
            self.supplier_combo.set('')  # Clear selection
            
            # Set new values
            self.supplier_combo['values'] = tuple(supplier_list)
            
            # Try to restore selection
            if current_selection and current_selection in supplier_list:
                self.supplier_combo.set(current_selection)
            
            # Force widget update
            self.supplier_combo.update_idletasks()
            
            return len(supplier_list)
            
        except Exception as e:
            logging.error(f"Error refreshing suppliers: {e}")
            messagebox.showerror("Error", f"Failed to refresh suppliers: {str(e)}")
            return 0

    def _add_supplier_now(self):

        dialog = tk.Toplevel(self.frame)
        dialog.title("✨ Add New Supplier")
        dialog.resizable(True, True)  # Allow resizing
        dialog.grab_set()
        dialog.transient(self.frame)
        
        # Get screen dimensions for proper sizing
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        
        # Set dialog size based on screen size (ensure it fits on screen)
        dialog_width = min(600, int(screen_width * 0.7))
        dialog_height = min(750, int(screen_height * 0.85))
        
        # Center dialog on screen
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Set minimum size to ensure usability
        dialog.minsize(550, 600)
        
        # Main container
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="Add New Supplier", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack()
        
        # Create main content frame with scrollbar
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar setup
        canvas = tk.Canvas(content_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # === FORM SECTIONS ===
        
        # 1. BASIC INFORMATION
        basic_frame = ttk.LabelFrame(scrollable_frame, text="📋 Basic Information", padding=15)
        basic_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Supplier Name (Required)
        ttk.Label(basic_frame, text="Supplier Name *", 
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(basic_frame, width=35, font=('Segoe UI', 10))
        name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        name_entry.focus()
        
        # Supplier Code
        ttk.Label(basic_frame, text="Supplier Code", 
                 font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        code_entry = ttk.Entry(basic_frame, width=35, font=('Segoe UI', 10))
        code_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Auto-generate supplier code
        import random
        auto_code = f"SUP{random.randint(1000, 9999)}"
        code_entry.insert(0, auto_code)
        
        # Contact Person
        ttk.Label(basic_frame, text="Contact Person", 
                 font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=5)
        contact_entry = ttk.Entry(basic_frame, width=35, font=('Segoe UI', 10))
        contact_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        basic_frame.columnconfigure(1, weight=1)
        
        # 2. CONTACT INFORMATION
        contact_frame = ttk.LabelFrame(scrollable_frame, text="📞 Contact Information", padding=15)
        contact_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Phone Number
        ttk.Label(contact_frame, text="Phone Number", 
                 font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        phone_entry = ttk.Entry(contact_frame, width=35, font=('Segoe UI', 10))
        phone_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Email Address
        ttk.Label(contact_frame, text="Email Address", 
                 font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        email_entry = ttk.Entry(contact_frame, width=35, font=('Segoe UI', 10))
        email_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        contact_frame.columnconfigure(1, weight=1)
        
        # 3. ADDRESS INFORMATION
        address_frame = ttk.LabelFrame(scrollable_frame, text="🏠 Address Information", padding=15)
        address_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Street Address
        ttk.Label(address_frame, text="Street Address", 
                 font=('Segoe UI', 10)).grid(row=0, column=0, sticky='nw', pady=5)
        address_text = tk.Text(address_frame, height=3, width=35, font=('Segoe UI', 10))
        address_text.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # City, State, Pincode in organized layout
        location_frame = ttk.Frame(address_frame)
        location_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=10)
        
        # City
        ttk.Label(location_frame, text="City:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', padx=5)
        city_entry = ttk.Entry(location_frame, width=15, font=('Segoe UI', 10))
        city_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        # State
        ttk.Label(location_frame, text="State:", font=('Segoe UI', 10)).grid(row=0, column=2, sticky='w', padx=5)
        state_entry = ttk.Entry(location_frame, width=15, font=('Segoe UI', 10))
        state_entry.grid(row=0, column=3, padx=5, sticky='ew')
        
        # Pincode
        ttk.Label(location_frame, text="Pincode:", font=('Segoe UI', 10)).grid(row=0, column=4, sticky='w', padx=5)
        pincode_entry = ttk.Entry(location_frame, width=10, font=('Segoe UI', 10))
        pincode_entry.grid(row=0, column=5, padx=5)
        
        # Configure location frame columns
        location_frame.columnconfigure(1, weight=1)
        location_frame.columnconfigure(3, weight=1)
        
        address_frame.columnconfigure(1, weight=1)
        
        # 4. BUSINESS INFORMATION
        business_frame = ttk.LabelFrame(scrollable_frame, text="💼 Business Information", padding=15)
        business_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # GST Number
        ttk.Label(business_frame, text="GST Number", 
                 font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        gst_entry = ttk.Entry(business_frame, width=35, font=('Segoe UI', 10))
        gst_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Tax ID
        ttk.Label(business_frame, text="Tax ID", 
                 font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        tax_id_entry = ttk.Entry(business_frame, width=35, font=('Segoe UI', 10))
        tax_id_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Credit Limit
        ttk.Label(business_frame, text="Credit Limit (₹)", 
                 font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=5)
        credit_entry = ttk.Entry(business_frame, width=35, font=('Segoe UI', 10))
        credit_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        credit_entry.insert(0, "0.00")
        
        # Payment Terms
        ttk.Label(business_frame, text="Payment Terms", 
                 font=('Segoe UI', 10)).grid(row=3, column=0, sticky='w', pady=5)
        payment_combo = ttk.Combobox(business_frame, width=32, font=('Segoe UI', 10), state="readonly")
        payment_combo['values'] = ('Cash on Delivery', 'Net 30 Days', 'Net 60 Days', 'Net 90 Days', 'Advance Payment')
        payment_combo.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        payment_combo.set('Net 30 Days')
        
        business_frame.columnconfigure(1, weight=1)
        
        # Status label for feedback
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        status_label = ttk.Label(status_frame, text="", font=('Segoe UI', 9))
        status_label.pack()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def validate_and_save():
            """Validate form data and save supplier"""
            # Clear status
            status_label.config(text="", foreground="black")
            
            # Get and validate data
            name = name_entry.get().strip()
            supplier_code = code_entry.get().strip()
            contact_person = contact_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            address = address_text.get('1.0', tk.END).strip()
            city = city_entry.get().strip()
            state = state_entry.get().strip()
            pincode = pincode_entry.get().strip()
            gst_number = gst_entry.get().strip()
            tax_id = tax_id_entry.get().strip()
            payment_terms = payment_combo.get()
            
            # Validation
            if not name:
                status_label.config(text="❌ Supplier name is required!", foreground="red")
                name_entry.focus()
                return
            
            if len(name) < 2:
                status_label.config(text="❌ Supplier name must be at least 2 characters!", foreground="red")
                name_entry.focus()
                return
            
            if not supplier_code:
                status_label.config(text="❌ Supplier code is required!", foreground="red")
                code_entry.focus()
                return
            
            # Validate phone if provided
            if phone and (len(phone) < 10 or not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit()):
                status_label.config(text="❌ Please enter a valid phone number (10+ digits)!", foreground="red")
                phone_entry.focus()
                return
            
            # Validate email if provided
            if email and '@' not in email:
                status_label.config(text="❌ Please enter a valid email address!", foreground="red")
                email_entry.focus()
                return
            
            # Validate credit limit
            try:
                credit_limit = float(credit_entry.get() or 0)
                if credit_limit < 0:
                    raise ValueError()
            except ValueError:
                status_label.config(text="❌ Please enter a valid credit limit!", foreground="red")
                credit_entry.focus()
                return
            
            # Validate pincode if provided
            if pincode and (len(pincode) != 6 or not pincode.isdigit()):
                status_label.config(text="❌ Pincode must be exactly 6 digits!", foreground="red")
                pincode_entry.focus()
                return
            
            try:
                # Show saving status
                status_label.config(text="💾 Saving supplier...", foreground="blue")
                dialog.update()
                
                # Create supplier data
                supplier_data = {
                    'supplier_code': supplier_code,
                    'name': name,
                    'contact_person': contact_person or None,
                    'phone': phone or None,
                    'email': email or None,
                    'address': address or None,
                    'city': city or None,
                    'state': state or None,
                    'pincode': pincode or None,
                    'gst_number': gst_number or None,
                    'tax_id': tax_id or None,
                    'payment_terms': payment_terms,
                    'credit_limit': credit_limit
                }
                
                # Create supplier using the model
                supplier_id = Supplier.create_supplier(**supplier_data)
                
                # Close dialog
                dialog.destroy()
                
                # Refresh suppliers in the inventory panel
                count = self._refresh_suppliers_now()
                
                # Select the new supplier
                new_supplier_text = f"{supplier_id} - {name}"
                if new_supplier_text in self.supplier_combo['values']:
                    self.supplier_combo.set(new_supplier_text)
                
                # Success message
                messagebox.showinfo("✅ Success", 
                                  f"Supplier '{name}' added successfully!\n\n"
                                  f"📋 Details:\n"
                                  f"• Supplier ID: {supplier_id}\n"
                                  f"• Supplier Code: {supplier_code}\n"
                                  f"• Contact: {contact_person or 'Not specified'}\n"
                                  f"• Phone: {phone or 'Not specified'}\n"
                                  f"• Total Suppliers: {count}")
                
            except Exception as e:
                status_label.config(text=f"❌ Error: {str(e)}", foreground="red")
                logging.error(f"Error adding supplier: {e}")
        
        def cancel():
            """Cancel and close dialog"""
            if messagebox.askyesno("Confirm", "Are you sure you want to cancel? All entered data will be lost."):
                dialog.destroy()
        
        def reset_form():
            """Reset all form fields"""
            name_entry.delete(0, tk.END)
            code_entry.delete(0, tk.END)
            code_entry.insert(0, f"SUP{random.randint(1000, 9999)}")
            contact_entry.delete(0, tk.END)
            phone_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            address_text.delete('1.0', tk.END)
            city_entry.delete(0, tk.END)
            state_entry.delete(0, tk.END)
            pincode_entry.delete(0, tk.END)
            gst_entry.delete(0, tk.END)
            tax_id_entry.delete(0, tk.END)
            credit_entry.delete(0, tk.END)
            credit_entry.insert(0, "0.00")
            payment_combo.set('Net 30 Days')
            status_label.config(text="")
            name_entry.focus()
        
        # Action buttons with improved styling
        ttk.Button(button_frame, text="💾 Save Supplier", command=validate_and_save, 
                  width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Reset Form", command=reset_form, 
                  width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=cancel, 
                  width=18).pack(side=tk.RIGHT, padx=5)
        
        # Key bindings for better UX
        dialog.bind('<Return>', lambda e: validate_and_save())
        dialog.bind('<Escape>', lambda e: cancel())
        dialog.bind('<Control-r>', lambda e: reset_form())
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="💡 Tips: Tab to navigate • Enter to save • Esc to cancel • Ctrl+R to reset",
                               font=('Segoe UI', 8), foreground="gray")
        instructions.pack(pady=(5, 0))
        
        # Ensure canvas scrolls to top
        canvas.yview_moveto(0)
        
        # Force focus on first field
        dialog.after(100, name_entry.focus)

    def create_action_buttons(self, parent):
        """Create action buttons with improved layout"""
        button_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main action buttons
        main_buttons = ttk.Frame(button_frame)
        main_buttons.pack(fill=tk.X)
        
        ttk.Button(main_buttons, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(main_buttons, text="Update Product", command=self.update_product).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(main_buttons, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Utility buttons
        util_buttons = ttk.Frame(button_frame)
        util_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(util_buttons, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=2)
        ttk.Button(util_buttons, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(util_buttons, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2)

    def create_alerts_section(self, parent):
        """Create alerts and notifications section"""
        alerts_frame = ttk.LabelFrame(parent, text="Alerts & Notifications", padding=10)
        alerts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Alert listbox with better styling
        self.alerts_listbox = tk.Listbox(alerts_frame, height=8, font=('Segoe UI', 9))
        alert_scrollbar = ttk.Scrollbar(alerts_frame, orient=tk.VERTICAL, command=self.alerts_listbox.yview)
        self.alerts_listbox.configure(yscrollcommand=alert_scrollbar.set)
        
        self.alerts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        alert_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Alert refresh button
        ttk.Button(alerts_frame, text="Refresh Alerts", command=self.check_alerts).pack(pady=(5, 0))

    def create_product_list(self, parent):
        """Create product list with improved search and filters"""
        # Better search and filter layout
        search_frame = ttk.LabelFrame(parent, text="Search & Filter", padding=8)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # First row - Search and Category
        row1 = ttk.Frame(search_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(row1, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 15))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Label(row1, text="Category:").pack(side=tk.LEFT)
        self.filter_category = ttk.Combobox(row1, values=['All'] + self.get_categories(), 
                                          width=15, state="readonly")
        self.filter_category.set('All')
        self.filter_category.pack(side=tk.LEFT, padx=(5, 15))
        self.filter_category.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Second row - Buttons
        row2 = ttk.Frame(search_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Button(row2, text="Search", command=self.search_products).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="Refresh", command=self.refresh_product_list).pack(side=tk.LEFT, padx=2)
        
        # Product tree view
        list_frame = ttk.LabelFrame(parent, text="Product Inventory", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Define columns with Indian currency
        columns = ('Barcode', 'Name', 'Category', 'Brand', 'Stock', 'Price (₹)', 'Expiry', 'Status')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure column headings and widths
        for col in columns:
            self.product_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            if col == 'Name':
                self.product_tree.column(col, width=150, minwidth=100)
            elif col == 'Category':
                self.product_tree.column(col, width=120, minwidth=80)
            else:
                self.product_tree.column(col, width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.product_tree.xview)
        self.product_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.product_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to edit
        self.product_tree.bind('<Double-1>', self.on_product_double_click)
        
        # Context menu
        self.create_context_menu()

    def create_context_menu(self):
        """Create right-click context menu for product list"""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Edit Product", command=self.edit_selected_product)
        self.context_menu.add_command(label="View Details", command=self.view_product_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Adjust Stock", command=self.adjust_stock)
        self.context_menu.add_command(label="Set Reorder Level", command=self.set_reorder_level)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Product", command=self.delete_selected_product)
        
        self.product_tree.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def get_categories(self):
        """Get comprehensive list of product categories for Indian market"""
        return [
            'Groceries', 'Vegetables', 'Fruits', 'Dairy Products', 'Meat & Fish',
            'Beverages', 'Snacks & Confectionery', 'Personal Care', 'Household Items',
            'Electronics', 'Spices & Condiments', 'Bakery Items', 'Frozen Foods',
            'Health & Beauty', 'Baby Products', 'Pet Supplies', 'Stationery',
            'Cleaning Supplies', 'Pharmacy', 'Organic Products'
        ]

    def get_suppliers(self):
        """Get list of suppliers"""
        try:
            suppliers = Supplier.get_all_suppliers()
            if suppliers:
                supplier_list = [f"{supplier.id} - {supplier.name}" for supplier in suppliers]
                logging.info(f"get_suppliers() returning {len(supplier_list)} suppliers")
                return supplier_list
            else:
                logging.warning("get_suppliers() - No suppliers found in database")
                return []
        except Exception as e:
            logging.error(f"Error in get_suppliers(): {e}")
            return []

    def scan_barcode(self):
        """Simulate barcode scanning"""
        import random
        barcode = f"{random.randint(100000000000, 999999999999)}"  # 12-digit barcode
        self.barcode_entry.delete(0, tk.END)
        self.barcode_entry.insert(0, barcode)
        messagebox.showinfo("Barcode Scan", f"Scanned barcode: {barcode}")

    def validate_and_format_date(self, date_string):
        """Ensure date is in YYYY-MM-DD format and valid"""
        if not date_string:
            return None
        
        # Convert DD-MM-YYYY to YYYY-MM-DD
        if '/' in date_string:
            date_string = date_string.replace('/', '-')
        
        # Handle DD-MM-YYYY format
        if '-' in date_string:
            parts = date_string.split('-')
            if len(parts) == 3 and len(parts[0]) == 2:
                # Convert DD-MM-YYYY to YYYY-MM-DD
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
        
        # Validate YYYY-MM-DD format
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return date_string
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use DD-MM-YYYY")
            return None


    def get_category_id_by_name(self, category_name):
        """Convert category name to category ID - THE FIX"""
        try:
            from database import get_db
            conn, cursor = get_db()
            
            cursor.execute("SELECT id FROM categories WHERE name = %s AND is_active = TRUE", 
                          (category_name,))
            result = cursor.fetchone()
            
            if result:
                cursor.close()
                return result[0]
            else:
                # If category doesn't exist, create it
                cursor.execute("INSERT INTO categories (name, is_active) VALUES (%s, TRUE)", 
                              (category_name,))
                category_id = cursor.lastrowid
                conn.commit()
                cursor.close()
                print(f"Created new category: {category_name} with ID: {category_id}")
                return category_id
                
        except Exception as e:
            print(f"Error getting category ID for '{category_name}': {e}")
            return None

    def add_product(self):
        """Add new product with comprehensive validation"""
        try:
            # Collect and validate form data
            product_data = self.get_form_data()
            
            # Validate required fields
            if not product_data['name'] or not product_data['barcode']:
                messagebox.showerror("Error", "Product name and barcode are required")
                return
            
            # Validate numeric fields
            if product_data['unit_price'] <= 0:
                messagebox.showerror("Error", "Selling price must be greater than 0")
                return
            
            # Validate expiry date
            if product_data['expiry_date']:
                validated_date = self.validate_and_format_date(product_data['expiry_date'])
                if validated_date is None:
                    return
                product_data['expiry_date'] = validated_date
            
            # Create product
            Product.create_product(**product_data)
            
            messagebox.showinfo("Success", "Product added successfully")
            self.clear_form()
            self.refresh_product_list()
            self.check_alerts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
            logging.error(f"Error adding product: {e}")

    def update_product(self):
        """Update selected product with validation"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to update")
            return
        
        try:
            # Get selected product details
            item = self.product_tree.item(selection[0])
            product_barcode = item['values'][0]
            
            # Get form data but EXCLUDE barcode from kwargs
            update_data = self.get_update_data()
            
            # Validate expiry date
            if update_data.get('expiry_date'):
                validated_date = self.validate_and_format_date(update_data['expiry_date'])
                if validated_date is None:
                    return
                update_data['expiry_date'] = validated_date
            
            # Update product - pass barcode as positional arg, rest as kwargs
            Product.update_product_by_barcode(product_barcode, **update_data)
            
            messagebox.showinfo("Success", "Product updated successfully")
            self.refresh_product_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")
            logging.error(f"Error updating product: {e}")

    def delete_product(self):
        """Delete selected product"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
        
        item = self.product_tree.item(selection[0])
        product_name = item['values'][1]
        
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete '{product_name}'?"):
            return
        
        try:
            product_barcode = item['values'][0]
            Product.delete_product_by_barcode(product_barcode)
            
            messagebox.showinfo("Success", "Product deleted successfully")
            self.clear_form()
            self.refresh_product_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {str(e)}")

    def get_form_data(self):

        description = self.description_entry.get('1.0', tk.END).strip()
        

        category_name = self.category_combo.get().strip()
        category_id = self.get_category_id_by_name(category_name)
        
        if not category_id:
            raise ValueError(f"Invalid category selected: {category_name}")
        
        return {
            'barcode': self.barcode_entry.get().strip(),
            'name': self.name_entry.get().strip(),
            'description': description if description else None,
            'category_id': category_id,  
            'brand': self.brand_entry.get().strip(),
            'unit_price': float(self.unit_price_entry.get() or 0),
            'cost_price': float(self.cost_price_entry.get() or 0),
            'quantity_in_stock': int(self.quantity_entry.get() or 0),
            'reorder_level': int(self.reorder_level_entry.get() or 0),
            'expiry_date': self.expiry_entry.get().strip() or None,
            'supplier_id': self.parse_supplier_id(self.supplier_combo.get()),
            'tax_rate': float(self.tax_rate_entry.get() or 18),
            'discount_rate': float(self.discount_rate_entry.get() or 0)
        }

    def get_update_data(self):

        description = self.description_entry.get('1.0', tk.END).strip()
        

        category_name = self.category_combo.get().strip()
        category_id = self.get_category_id_by_name(category_name)
        
        if not category_id:
            raise ValueError(f"Invalid category selected: {category_name}")
        
        return {
            # DON'T include barcode here - it's passed separately
            'name': self.name_entry.get().strip(),
            'description': description if description else None,
            'category_id': category_id, 
            'brand': self.brand_entry.get().strip(),
            'unit_price': float(self.unit_price_entry.get() or 0),
            'cost_price': float(self.cost_price_entry.get() or 0),
            'quantity_in_stock': int(self.quantity_entry.get() or 0),
            'reorder_level': int(self.reorder_level_entry.get() or 0),
            'expiry_date': self.expiry_entry.get().strip() or None,
            'supplier_id': self.parse_supplier_id(self.supplier_combo.get()),
            'tax_rate': float(self.tax_rate_entry.get() or 18),
            'discount_rate': float(self.discount_rate_entry.get() or 0)
        }

    def parse_supplier_id(self, supplier_text):
        """Parse supplier ID from combo selection"""
        if supplier_text and ' - ' in supplier_text:
            try:
                return int(supplier_text.split(' - ')[0])
            except ValueError:
                return None
        return None

    def clear_form(self):
        """Clear all form fields"""
        self.barcode_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete('1.0', tk.END)
        self.category_combo.current(0)  # Reset to first category
        self.brand_entry.delete(0, tk.END)
        self.unit_price_entry.delete(0, tk.END)
        self.cost_price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.reorder_level_entry.delete(0, tk.END)
        self.expiry_entry.delete(0, tk.END)
        self.supplier_combo.set('')
        self.tax_rate_entry.delete(0, tk.END)
        self.tax_rate_entry.insert(0, "18.0")
        self.discount_rate_entry.delete(0, tk.END)
        self.discount_rate_entry.insert(0, "0.0")

    def refresh_product_list(self):
        """Refresh product list with Indian currency format"""
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        try:
            products = Product.get_all_products()
            for product in products:
                # Determine status
                status = "Active"
                if product.quantity_in_stock <= product.reorder_level:
                    status = "Low Stock"
                if product.expiry_date:
                    try:
                        expiry = datetime.strptime(str(product.expiry_date), '%Y-%m-%d')
                        if expiry <= datetime.now() + timedelta(days=7):
                            status = "Expiring Soon"
                        if expiry <= datetime.now():
                            status = "Expired"
                    except:
                        pass
                
                self.product_tree.insert('', tk.END, values=(
                    product.barcode or '',
                    product.name or '',
                    product.category or '',
                    product.brand or '',
                    product.quantity_in_stock,
                    f"₹{product.unit_price:.2f}",  # Indian Rupee format
                    product.expiry_date or 'N/A',
                    status
                ))
        except Exception as e:
            logging.error(f"Error refreshing product list: {e}")

    def check_alerts(self):
        """Check for low stock and expiring products"""
        self.alerts_listbox.delete(0, tk.END)
        
        try:
            # Low stock alerts
            low_stock = Product.get_low_stock_products()
            for product in low_stock:
                alert_msg = f"🔸 LOW STOCK: {product[2]} - Only {product[3]} units left (Reorder: {product[4]})"
                self.alerts_listbox.insert(tk.END, alert_msg)
            
            # Expiring products
            expiring = Product.get_expiring_products(7)
            for product in expiring:
                alert_msg = f"⏰ EXPIRING: {product[2]} - Expires on {product[3]} ({product[4]} units)"
                self.alerts_listbox.insert(tk.END, alert_msg)
            
            if not low_stock and not expiring:
                self.alerts_listbox.insert(tk.END, "✅ No alerts at this time - All products are well stocked!")
                
        except Exception as e:
            self.alerts_listbox.insert(tk.END, f"❌ Error loading alerts: {str(e)}")
            logging.error(f"Error checking alerts: {e}")

    def on_search_change(self, event=None):
        """Handle real-time search as user types"""
        search_term = self.search_entry.get().strip()
        if len(search_term) >= 3:  # Start search after 3 characters
            self.search_products()
        elif len(search_term) == 0:
            self.refresh_product_list()

    def search_products(self):
        """Search products based on criteria"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.refresh_product_list()
            return
        
        try:
            products = Product.search_products(search_term)
            
            # Clear current list
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)
            
            # Populate with search results
            for product in products:
                status = "Active"
                if product.quantity_in_stock <= product.reorder_level:
                    status = "Low Stock"
                
                self.product_tree.insert('', tk.END, values=(
                    product.barcode or '',
                    product.name or '',
                    product.category or '',
                    product.brand or '',
                    product.quantity_in_stock,
                    f"₹{product.unit_price:.2f}",
                    product.expiry_date or 'N/A',
                    status
                ))
                
            if not products:
                # Insert "no results" message
                self.product_tree.insert('', tk.END, values=(
                    '', 'No products found', '', '', '', '', '', ''
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def clear_search(self):
        """Clear search and refresh full list"""
        self.search_entry.delete(0, tk.END)
        self.filter_category.set('All')
        self.refresh_product_list()

    def apply_filters(self, event=None):
        """Apply category filter"""
        category = self.filter_category.get()
        
        # Clear current list
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        try:
            products = Product.get_all_products()
            
            for product in products:
                if category == 'All' or product.category == category:
                    status = "Active"
                    if product.quantity_in_stock <= product.reorder_level:
                        status = "Low Stock"
                    
                    self.product_tree.insert('', tk.END, values=(
                        product.barcode or '',
                        product.name or '',
                        product.category or '',
                        product.brand or '',
                        product.quantity_in_stock,
                        f"₹{product.unit_price:.2f}",
                        product.expiry_date or 'N/A',
                        status
                    ))
                    
        except Exception as e:
            logging.error(f"Error filtering products: {e}")

    def sort_by_column(self, col):
        """Sort tree view by column"""
        # Get all items
        items = [(self.product_tree.item(child)['values'], child) 
                for child in self.product_tree.get_children()]
        
        # Find column index
        columns = ('Barcode', 'Name', 'Category', 'Brand', 'Stock', 'Price (₹)', 'Expiry', 'Status')
        col_index = columns.index(col)
        
        # Sort items
        try:
            if col == 'Stock':
                items.sort(key=lambda x: int(x[0][col_index]) if x[0][col_index] else 0)
            elif col == 'Price (₹)':
                items.sort(key=lambda x: float(x[0][col_index].replace('₹', '')) if x[0][col_index].startswith('₹') else 0)
            else:
                items.sort(key=lambda x: str(x[0][col_index]))
            
            # Rearrange items in tree
            for index, (values, child) in enumerate(items):
                self.product_tree.move(child, '', index)
                
        except Exception as e:
            logging.error(f"Error sorting by column {col}: {e}")

    def on_product_double_click(self, event):
        """Handle double-click on product"""
        self.edit_selected_product()

    def edit_selected_product(self):
        """Edit selected product - load data into form"""
        selection = self.product_tree.selection()
        if not selection:
            return
        
        try:
            # Get product data and load into form
            item = self.product_tree.item(selection[0])
            values = item['values']
            
            # Only proceed if it's a valid product row
            if len(values) >= 8 and values[1] != 'No products found':
                barcode = values[0]
                
                # Fetch full product details
                products = Product.search_products(barcode) if barcode else []
                if products:
                    product = products[0]
                    
                    # Clear and populate form
                    self.clear_form()
                    
                    self.barcode_entry.insert(0, product.barcode or '')
                    self.name_entry.insert(0, product.name or '')
                    
                    if product.description:
                        self.description_entry.insert('1.0', product.description)
                    
                    if product.category and product.category in self.get_categories():
                        self.category_combo.set(product.category)
                    
                    self.brand_entry.insert(0, product.brand or '')
                    self.unit_price_entry.insert(0, str(product.unit_price or 0))
                    self.cost_price_entry.insert(0, str(product.cost_price or 0))
                    self.quantity_entry.insert(0, str(product.quantity_in_stock or 0))
                    self.reorder_level_entry.insert(0, str(product.reorder_level or 0))
                    
                    if product.expiry_date:
                        # Convert YYYY-MM-DD to DD-MM-YYYY for display
                        try:
                            date_obj = datetime.strptime(str(product.expiry_date), '%Y-%m-%d')
                            display_date = date_obj.strftime('%d-%m-%Y')
                            self.expiry_entry.insert(0, display_date)
                        except:
                            self.expiry_entry.insert(0, str(product.expiry_date))
                    
                    # Load supplier if available
                    if hasattr(product, 'supplier_id') and product.supplier_id:
                        # First reload suppliers to ensure we have the latest list
                        self._refresh_suppliers_now()
                        suppliers = self.supplier_combo['values']
                        for supplier in suppliers:
                            if supplier.startswith(f"{product.supplier_id} -"):
                                self.supplier_combo.set(supplier)
                                break
                    
                    self.tax_rate_entry.delete(0, tk.END)
                    self.tax_rate_entry.insert(0, str(product.tax_rate or 18))
                    
                    self.discount_rate_entry.delete(0, tk.END)
                    self.discount_rate_entry.insert(0, str(product.discount_rate or 0))
                    
        except Exception as e:
            logging.error(f"Error editing product: {e}")
            messagebox.showerror("Error", f"Failed to load product data: {str(e)}")

    def view_product_details(self):
        """View detailed product information"""
        selection = self.product_tree.selection()
        if not selection:
            return
        
        item = self.product_tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 8 and values[1] != 'No products found':
            details = f"""
Product Details:
═══════════════════════════════════════
Barcode: {values[0]}
Name: {values[1]}
Category: {values[2]}
Brand: {values[3]}
Stock Quantity: {values[4]}
Price: {values[5]}
Expiry Date: {values[6]}
Status: {values[7]}
═══════════════════════════════════════
            """
            messagebox.showinfo("Product Details", details)

    def adjust_stock(self):
        """Adjust stock for selected product"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product")
            return
        
        item = self.product_tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 8 and values[1] != 'No products found':
            current_stock = values[4]
            product_name = values[1]
            
            # Create stock adjustment dialog
            adjustment_window = tk.Toplevel(self.frame)
            adjustment_window.title("Stock Adjustment")
            adjustment_window.geometry("300x200")
            adjustment_window.grab_set()
            
            ttk.Label(adjustment_window, text=f"Product: {product_name}").pack(pady=10)
            ttk.Label(adjustment_window, text=f"Current Stock: {current_stock}").pack(pady=5)
            
            ttk.Label(adjustment_window, text="Adjustment:").pack(pady=5)
            adjustment_entry = ttk.Entry(adjustment_window, width=20)
            adjustment_entry.pack(pady=5)
            
            ttk.Label(adjustment_window, text="Reason:").pack(pady=5)
            reason_entry = ttk.Entry(adjustment_window, width=30)
            reason_entry.pack(pady=5)
            
            def apply_adjustment():
                try:
                    adjustment = int(adjustment_entry.get())
                    reason = reason_entry.get().strip()
                    
                    if not reason:
                        messagebox.showerror("Error", "Please provide a reason")
                        return
                    
                    messagebox.showinfo("Success", f"Stock adjusted by {adjustment} units\nReason: {reason}")
                    adjustment_window.destroy()
                    self.refresh_product_list()
                    
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number")
            
            ttk.Button(adjustment_window, text="Apply", command=apply_adjustment).pack(pady=10)
            ttk.Button(adjustment_window, text="Cancel", command=adjustment_window.destroy).pack()

    def set_reorder_level(self):
        """Set reorder level for selected product"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product")
            return
        
        item = self.product_tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 8 and values[1] != 'No products found':
            product_name = values[1]
            
            new_level = simpledialog.askinteger(
                "Set Reorder Level",
                f"Product: {product_name}\nEnter new reorder level:",
                minvalue=0,
                maxvalue=10000
            )
            
            if new_level is not None:
                messagebox.showinfo("Success", f"Reorder level set to {new_level}")
                self.refresh_product_list()

    def delete_selected_product(self):
        """Delete selected product via context menu"""
        self.delete_product()

    def import_csv(self):
        """Import products from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    imported_count = 0
                    error_count = 0
                    
                    for row in csv_reader:
                        try:
                            # Expected CSV columns: barcode, name, category, brand, unit_price, cost_price, quantity_in_stock, reorder_level
                            product_data = {
                                'barcode': row.get('barcode', ''),
                                'name': row.get('name', ''),
                                'description': row.get('description', ''),
                                'category': row.get('category', ''),
                                'brand': row.get('brand', ''),
                                'unit_price': float(row.get('unit_price', 0)),
                                'cost_price': float(row.get('cost_price', 0)),
                                'quantity_in_stock': int(row.get('quantity_in_stock', 0)),
                                'reorder_level': int(row.get('reorder_level', 0)),
                                'tax_rate': float(row.get('tax_rate', 18)),
                                'discount_rate': float(row.get('discount_rate', 0))
                            }
                            
                            if product_data['name'] and product_data['barcode']:
                                Product.create_product(**product_data)
                                imported_count += 1
                        except Exception as e:
                            logging.error(f"Error importing row: {e}")
                            error_count += 1
                    
                    messagebox.showinfo("Import Complete", 
                                      f"Successfully imported: {imported_count} products\n"
                                      f"Errors: {error_count} products")
                    self.refresh_product_list()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")

    def export_csv(self):
        """Export products to CSV file"""
        file_path = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Write headers
                    writer.writerow(['Barcode', 'Name', 'Category', 'Brand', 'Stock', 'Price', 'Expiry', 'Status'])
                    
                    # Write product data
                    for child in self.product_tree.get_children():
                        values = self.product_tree.item(child)['values']
                        if len(values) >= 8 and values[1] != 'No products found':
                            writer.writerow(values)
                    
                    messagebox.showinfo("Success", f"Products exported to {file_path}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    def refresh(self):
        """Refresh panel data"""
        self.refresh_product_list()
        self.check_alerts()
        # Also refresh suppliers when panel is refreshed
        self._refresh_suppliers_now()
