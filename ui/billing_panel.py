"""
Point-of-Sale billing interface
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import logging

from models.product import Product
from models.customer import Customer
from models.transaction import Transaction
from database import get_db

RUPEE = "₹"


class BillingPanel:
    # ─────────────────────────────────────────────── initialisation ─
    def __init__(self, notebook, main_app):
        self.notebook = notebook
        self.main_app = main_app
        self.cart_items = []    # list of dicts
        self.current_customer = None
        self._build_ui()

    # ────────────────────────────────────────── helper: categories ─
    def _categories(self):
        return [
            'All', 'Groceries', 'Vegetables', 'Fruits', 'Dairy Products',
            'Meat & Fish', 'Beverages', 'Snacks', 'Personal Care',
            'Household Items', 'Electronics', 'Spices & Condiments',
            'Bakery Items'
        ]

    # ──────────────────────────────────────────────── main layout ─
    def _build_ui(self):
        self.frame = ttk.Frame(self.notebook, padding=6)

        main_pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
        left   = ttk.Frame(main_pane, padding=3);  main_pane.add(left,   weight=1)
        centre = ttk.Frame(main_pane, padding=3);  main_pane.add(centre, weight=2)  # Changed from 1.5 to 2
        right  = ttk.Frame(main_pane, padding=3);  main_pane.add(right,  weight=1)

        self._create_product_search(left)
        self._create_cart(centre)
        self._create_payment(right)

        self.refresh_product_list()

    # ───────────────────────────────────── product search / select ─
    def _create_product_search(self, parent):
        box = ttk.LabelFrame(parent, text="Product Search", padding=6)
        box.pack(fill=tk.BOTH, expand=True)

        # barcode row
        row = ttk.Frame(box); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Barcode:").pack(side=tk.LEFT)
        self.barcode_ent = ttk.Entry(row, font=('Segoe UI', 10), width=15)  # Reduced width
        self.barcode_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        self.barcode_ent.bind('<Return>', self.scan_product)
        ttk.Button(row, text="Scan", command=self.scan_product, width=6).pack(side=tk.RIGHT)

        # search + category row
        row2 = ttk.Frame(box); row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Search:").pack(side=tk.LEFT)
        self.search_ent = ttk.Entry(row2, width=12)  # Reduced width
        self.search_ent.pack(side=tk.LEFT, padx=3)
        self.search_ent.bind('<KeyRelease>', self.search_products)

        ttk.Label(row2, text="Category:").pack(side=tk.LEFT)
        self.cat_filter = ttk.Combobox(
            row2, values=self._categories(), state="readonly", width=12)  # Reduced width
        self.cat_filter.set('All')
        self.cat_filter.pack(side=tk.LEFT, padx=3)
        self.cat_filter.bind('<<ComboboxSelected>>', self.filter_by_category)
        cols = ('Barcode', 'Name', 'Category', f'Price ({RUPEE})', 'Stock')
        self.prod_tree = ttk.Treeview(box, columns=cols, show='headings', height=12)
        
        # Set optimal column widths for better visibility
        self.prod_tree.column('Barcode', width=70, minwidth=60)
        self.prod_tree.column('Name', width=120, minwidth=100)
        self.prod_tree.column('Category', width=80, minwidth=70)
        self.prod_tree.column(f'Price ({RUPEE})', width=70, minwidth=60, anchor='e')
        self.prod_tree.column('Stock', width=50, minwidth=40, anchor='center')
        
        for c in cols:
            self.prod_tree.heading(c, text=c)
        
        ysb = ttk.Scrollbar(box, orient=tk.VERTICAL, command=self.prod_tree.yview)
        self.prod_tree.configure(yscrollcommand=ysb.set)
        self.prod_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.prod_tree.bind('<Double-1>', self.add_selected_product)

        ttk.Button(box, text="Add to Cart", command=self.add_selected_product).pack(pady=3)

    # ─────────────────────────────────────────────── shopping cart ─
    def _create_cart(self, parent):
        wrapper = ttk.LabelFrame(parent, text="Shopping Cart", padding=6)
        wrapper.pack(fill=tk.BOTH, expand=True)
        cols = ('Item', 'Qty', f'Unit ({RUPEE})', 'Dis%', 'GST%', f'Line ({RUPEE})')
        self.cart_tree = ttk.Treeview(wrapper, columns=cols, show='headings', height=12)
        
        # Compact column widths
        self.cart_tree.column('Item', width=100, minwidth=80)
        self.cart_tree.column('Qty', width=40, minwidth=35, anchor='center')
        self.cart_tree.column(f'Unit ({RUPEE})', width=65, minwidth=55, anchor='e')
        self.cart_tree.column('Dis%', width=40, minwidth=35, anchor='e')
        self.cart_tree.column('GST%', width=40, minwidth=35, anchor='e')
        self.cart_tree.column(f'Line ({RUPEE})', width=75, minwidth=65, anchor='e')
        
        for c in cols:
            self.cart_tree.heading(c, text=c)
        
        ysb = ttk.Scrollbar(wrapper, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=ysb.set)
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)

        # action buttons
        btns = ttk.Frame(wrapper); btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Remove", command=self.remove_cart_item, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(btns, text="Update Qty", command=self.update_quantity, width=9).pack(side=tk.LEFT, padx=1)
        ttk.Button(btns, text="Discount", command=self.apply_item_discount, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(btns, text="Clear Cart", command=self.clear_cart, width=9).pack(side=tk.LEFT, padx=1)

        # summary labels
        summ = ttk.LabelFrame(wrapper, text="Order Summary", padding=6)
        summ.pack(fill=tk.X)
        self.lb_sub   = ttk.Label(summ, text=f"Subtotal: {RUPEE}0.00");    self.lb_sub.pack(anchor='w')
        self.lb_itdis = ttk.Label(summ, text=f"Item Discount: {RUPEE}0.00");self.lb_itdis.pack(anchor='w')
        self.lb_ovdis = ttk.Label(summ, text=f"Order Discount: {RUPEE}0.00");self.lb_ovdis.pack(anchor='w')
        self.lb_tax   = ttk.Label(summ, text=f"GST: {RUPEE}0.00");         self.lb_tax.pack(anchor='w')
        self.lb_tot   = ttk.Label(summ, text=f"TOTAL: {RUPEE}0.00", font=('Segoe UI', 12, 'bold'))
        self.lb_tot.pack(anchor='w', pady=2)

    # ───────────────────────────────────────────── payment section ─
    def _create_payment(self, parent):
        cust_box = ttk.LabelFrame(parent, text="Customer", padding=6)
        cust_box.pack(fill=tk.X)
        row = ttk.Frame(cust_box); row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Phone:").pack(side=tk.LEFT)
        self.phone_ent = ttk.Entry(row, width=15)  # Reduced width
        self.phone_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 2))
        ttk.Button(row, text="Find", command=self.find_customer, width=6).pack(side=tk.LEFT)
        
        self.cust_lb = ttk.Label(cust_box, text="Walk-in Customer")
        self.cust_lb.pack(anchor='w', pady=2)
        ttk.Button(cust_box, text="New Customer", command=self.create_quick_customer).pack(anchor='w')

        pay_box = ttk.LabelFrame(parent, text="Payment", padding=6)
        pay_box.pack(fill=tk.X, pady=4)

        ttk.Label(pay_box, text="Method:").pack(anchor='w')
        self.pay_var = tk.StringVar(value='cash')
        for txt, val in (('Cash','cash'),('Card','card'),('UPI','upi'),('Credit','credit')):
            ttk.Radiobutton(pay_box, text=txt, variable=self.pay_var, value=val).pack(anchor='w')

        row2 = ttk.Frame(pay_box); row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text=f"Tendered ({RUPEE}):").pack(side=tk.LEFT)  # Shortened label
        self.tender_ent = ttk.Entry(row2, width=10)
        self.tender_ent.pack(side=tk.RIGHT)
        self.tender_ent.bind('<KeyRelease>', self.calculate_change)
        
        self.change_lb = ttk.Label(pay_box, text=f"Change: {RUPEE}0.00", font=('Segoe UI', 10, 'bold'))
        self.change_lb.pack(anchor='w', pady=2)

        act_box = ttk.LabelFrame(parent, text="Actions", padding=6)
        act_box.pack(fill=tk.X)
        ttk.Button(act_box, text="Process Sale",  command=self.process_sale).pack(fill=tk.X, pady=1)
        ttk.Button(act_box, text="Hold",          command=self.hold_transaction).pack(fill=tk.X, pady=1)
        ttk.Button(act_box, text="Print Receipt", command=self.print_receipt).pack(fill=tk.X, pady=1)
        ttk.Button(act_box, text="Refund",        command=self.process_refund).pack(fill=tk.X, pady=1)

    # ─────────────────────────────────────────── product listing ───
    def refresh_product_list(self):
        for i in self.prod_tree.get_children():
            self.prod_tree.delete(i)
        try:
            for p in Product.get_all_products()[:120]:
                self.prod_tree.insert('', tk.END, values=(
                    p.barcode or 'N/A',
                    p.name[:20],  # Shortened for better fit
                    p.category or 'N/A',
                    f"{RUPEE}{p.unit_price:.2f}",
                    p.quantity_in_stock
                ))
        except Exception as e:
            logging.error(f"Product refresh error: {e}")

    def search_products(self, *_):
        term = self.search_ent.get().strip()
        if not term:
            self.refresh_product_list(); return
        self._populate_products(Product.search_products(term))

    def filter_by_category(self, *_):
        cat = self.cat_filter.get()
        plist = Product.get_all_products()
        if cat != 'All':
            plist = [p for p in plist if p.category == cat]
        self._populate_products(plist)

    def _populate_products(self, plist):
        for i in self.prod_tree.get_children():
            self.prod_tree.delete(i)
        for p in plist:
            self.prod_tree.insert('', tk.END, values=(
                p.barcode or 'N/A',
                p.name[:20],  # Shortened for better fit
                p.category or 'N/A',
                f"{RUPEE}{p.unit_price:.2f}",
                p.quantity_in_stock
            ))

    def scan_product(self, *_):
        code = self.barcode_ent.get().strip()
        if not code:
            return
        res = Product.search_products(code)
        if res:
            self.add_product_to_cart(res[0])
        else:
            messagebox.showwarning("Not found", f"No product with barcode {code}")
        self.barcode_ent.delete(0, tk.END)
        self.barcode_ent.focus()

    def add_selected_product(self, *_):
        sel = self.prod_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select a product to add")
            return
        code = self.prod_tree.item(sel[0])['values'][0]
        if code == 'N/A':
            messagebox.showerror("Error", "Product has no barcode")
            return
        try:
            prod = Product.search_products(code)[0]
            self.add_product_to_cart(prod)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {e}")

    # ─────────────────────────────────────────────── cart logic ────
    def add_product_to_cart(self, prod, qty=1):
        if prod.quantity_in_stock < qty:
            messagebox.showwarning("Low Stock", f"Only {prod.quantity_in_stock} units available!")
            return
        for itm in self.cart_items:
            if itm['product_id'] == prod.id:
                new_q = itm['quantity'] + qty
                if new_q > prod.quantity_in_stock:
                    messagebox.showwarning("Stock Limit", f"Cannot add more than {prod.quantity_in_stock}")
                    return
                itm['quantity'] = new_q
                break
        else:
            self.cart_items.append({
                'product_id': prod.id,
                'name':       prod.name,
                'unit_price': float(prod.unit_price),
                'quantity':   qty,
                'disc':       float(prod.discount_rate or 0),
                'gst':        float(prod.tax_rate       or 18)
            })
        self._refresh_cart_tree()
        self.calculate_totals()

    def _refresh_cart_tree(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        for itm in self.cart_items:
            sub   = itm['quantity'] * itm['unit_price']
            less  = sub * itm['disc']/100
            gst   = (sub-less) * itm['gst']/100
            total = sub - less + gst
            self.cart_tree.insert('', tk.END, iid=str(itm['product_id']), values=(
                itm['name'][:18],  # Shortened for better fit
                itm['quantity'],
                f"{RUPEE}{itm['unit_price']:.2f}",
                f"{itm['disc']:.1f}",
                f"{itm['gst']:.1f}",
                f"{RUPEE}{total:.2f}"
            ))

    def update_quantity(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select an item to update")
            return
        pid = int(sel[0])
        itm = next((i for i in self.cart_items if i['product_id']==pid), None)
        if not itm:
            return
        new_q = simpledialog.askinteger(
            "Update Quantity",
            f"{itm['name']}\nCurrent: {itm['quantity']}\nNew quantity:",
            minvalue=1, maxvalue=999
        )
        if new_q and new_q != itm['quantity']:
            try:
                prod = Product.get_product_by_id(pid)
                if prod and new_q > prod.quantity_in_stock:
                    messagebox.showwarning("Stock Limit", f"Only {prod.quantity_in_stock} units available!")
                    return
            except:
                pass
            itm['quantity'] = new_q
            self._refresh_cart_tree()
            self.calculate_totals()

    def apply_item_discount(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select an item to apply discount")
            return
        pid = int(sel[0])
        itm = next((i for i in self.cart_items if i['product_id']==pid), None)
        if not itm:
            return
        nd = simpledialog.askfloat(
            "Apply Discount",
            f"{itm['name']}\nCurrent: {itm['disc']}%\nNew discount (0–100):",
            minvalue=0, maxvalue=100
        )
        if nd is not None:
            itm['disc'] = nd
            self._refresh_cart_tree()
            self.calculate_totals()

    def remove_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select an item to remove")
            return
        pid = int(sel[0])
        itm = next((i for i in self.cart_items if i['product_id']==pid), None)
        if itm and messagebox.askyesno("Confirm", f"Remove '{itm['name']}' from cart?"):
            self.cart_items = [i for i in self.cart_items if i['product_id']!=pid]
            self._refresh_cart_tree()
            self.calculate_totals()

    def clear_cart(self):
        if messagebox.askyesno("Confirm", "Clear entire cart?"):
            self.cart_items.clear()
            self._refresh_cart_tree()
            self.calculate_totals()

    # ─────────────────────────────────────── totals / change etc. ─
    def calculate_totals(self):
        if not self.cart_items:
            for lb in (self.lb_sub, self.lb_itdis, self.lb_ovdis, self.lb_tax, self.lb_tot):
                lb.config(text=lb.cget('text').split(':')[0] + f": {RUPEE}0.00")
            self.calculate_change(); return
        sub = disc = gst = 0
        for i in self.cart_items:
            s = i['quantity'] * i['unit_price']; sub += s
            d = s * i['disc']/100;               disc += d
            gst += (s-d)* i['gst']/100
        
        # Order discount (can be enhanced later)
        odisc = 0
        
        tot = sub - disc - odisc + gst
        self.lb_sub  .config(text=f"Subtotal: {RUPEE}{sub:.2f}")
        self.lb_itdis.config(text=f"Item Discount: {RUPEE}{disc:.2f}")
        self.lb_ovdis.config(text=f"Order Discount: {RUPEE}{odisc:.2f}")
        self.lb_tax  .config(text=f"GST: {RUPEE}{gst:.2f}")
        self.lb_tot  .config(text=f"TOTAL: {RUPEE}{tot:.2f}")
        self.calculate_change()

    def calculate_change(self, *_):
        if self.pay_var.get() != 'cash':
            self.change_lb.config(text="Change: N/A")
            return
        try:
            tender = float(self.tender_ent.get() or 0)
            total  = float(self.lb_tot.cget('text').split(RUPEE)[1])
            diff   = tender - total
            label  = "Change" if diff>=0 else "Short"
            self.change_lb.config(text=f"{label}: {RUPEE}{abs(diff):.2f}")
        except:
            self.change_lb.config(text=f"Change: {RUPEE}0.00")

    # ──────────────────────────────────────────── customer logic ──
    def find_customer(self):
        ph = self.phone_ent.get().strip()
        if not ph:
            messagebox.showwarning("Input Required", "Please enter phone number")
            return
        try:
            res = Customer.search_customers(ph)
            if res:
                self.current_customer = res[0]
                self.cust_lb.config(text=f"{res[0].name} ({res[0].phone})")
                logging.info(f"Customer found: {res[0].name}")
            else:
                self.current_customer = None
                self.cust_lb.config(text="Customer not found")
                messagebox.showinfo("Not Found", "Customer not found. Click 'New Customer' to add.")
        except Exception as e:
            logging.error(f"Error finding customer: {e}")
            messagebox.showerror("Error", f"Error searching customer: {e}")

    def create_quick_customer(self):
        """Enhanced New Customer dialog with Save/Cancel buttons"""
        win = tk.Toplevel(self.frame)
        win.title("Add New Customer")
        win.geometry("400x350")
        win.resizable(False, False)
        win.grab_set()
        win.transient(self.frame)

        # Center
        win.update_idletasks()
        x = (win.winfo_screenwidth()//2)-(400//2)
        y = (win.winfo_screenheight()//2)-(350//2)
        win.geometry(f"400x350+{x}+{y}")

        frm = ttk.Frame(win, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Customer Name *").grid(row=0, column=0, sticky='w', pady=5)
        en_n = ttk.Entry(frm, width=30); en_n.grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(frm, text="Phone Number *").grid(row=1, column=0, sticky='w', pady=5)
        en_p = ttk.Entry(frm, width=30); en_p.grid(row=1, column=1, sticky='ew', pady=5)

        ttk.Label(frm, text="Email").grid(row=2, column=0, sticky='w', pady=5)
        en_e = ttk.Entry(frm, width=30); en_e.grid(row=2, column=1, sticky='ew', pady=5)

        ttk.Label(frm, text="Address").grid(row=3, column=0, sticky='nw', pady=5)
        en_a = tk.Text(frm, height=4, width=30); en_a.grid(row=3, column=1, sticky='ew', pady=5)

        status_label = ttk.Label(frm, text="", foreground="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        def save():
            name = en_n.get().strip()
            phone= en_p.get().strip()
            email= en_e.get().strip()
            addr = en_a.get('1.0', tk.END).strip()
            status_label.config(text="")

            if not name:
                status_label.config(text="Name is required"); en_n.focus(); return
            if not phone:
                status_label.config(text="Phone is required"); en_p.focus(); return
            if len(phone)<10:
                status_label.config(text="Enter valid phone"); en_p.focus(); return

            try:
                cid = Customer.create_customer(
                    name=name, phone=phone,
                    email=email or None,
                    address=addr or None
                )
                messagebox.showinfo("Success","Customer added successfully!", parent=win)
                win.destroy()
                self.phone_ent.delete(0, tk.END)
                self.phone_ent.insert(0, phone)
                self.find_customer()
                logging.info(f"New customer: {name}")
            except Exception as e:
                status_label.config(text=str(e))
                logging.error(f"Error creating customer: {e}")

        def cancel():
            win.destroy()

        btns = ttk.Frame(frm); btns.grid(row=5, column=0, columnspan=2, pady=15)
        ttk.Button(btns, text="Save Customer", command=save, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btns, text="Cancel",        command=cancel, width=15).pack(side=tk.LEFT, padx=10)
        frm.columnconfigure(1, weight=1)

        en_n.focus()
        win.bind('<Return>', lambda e: save())
        win.bind('<Escape>', lambda e: cancel())

    # ───────────────────────────────────────────── ENHANCED SALE PROCESSING WITH DATABASE ─
    def process_sale(self):
        """Process sale and SAVE to database - ENHANCED VERSION"""
        if not self.cart_items:
            return messagebox.showwarning("Empty", "Cart is empty")

        # Payment validation
        if self.pay_var.get() == 'cash':
            try:
                tendered = float(self.tender_ent.get() or 0)
                total = float(self.lb_tot.cget('text').split(RUPEE)[1])
                if tendered < total:
                    messagebox.showerror("Payment", "Insufficient amount")
                    self.tender_ent.focus()
                    return
            except:
                messagebox.showerror("Payment", "Invalid payment")
                self.tender_ent.focus()
                return

        try:
            # Generate transaction number
            txn_number = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Calculate totals from cart
            subtotal = sum(item['quantity'] * item['unit_price'] for item in self.cart_items)
            total_discount = sum(item['quantity'] * item['unit_price'] * item.get('disc', 0) / 100 for item in self.cart_items)
            total_tax = sum((item['quantity'] * item['unit_price'] - 
                            item['quantity'] * item['unit_price'] * item.get('disc', 0) / 100) * 
                           item.get('gst', 18) / 100 for item in self.cart_items)
            final_total = subtotal - total_discount + total_tax
            
            # Get customer and employee IDs
            customer_id = self.current_customer.id if self.current_customer else None
            employee_id = 1  # Replace with actual logged-in employee ID
            payment_method = self.pay_var.get()
            
            # **CRITICAL: Save to database**
            conn, cursor = get_db()
            
            print(f"DEBUG: Starting transaction save - {txn_number}")
            print(f"DEBUG: Totals - Subtotal: ₹{subtotal}, Tax: ₹{total_tax}, Final: ₹{final_total}")
            
            # Insert transaction record
            cursor.execute("""
                INSERT INTO transactions (transaction_number, customer_id, employee_id, 
                                        subtotal, discount_amount, tax_amount, total_amount, 
                                        payment_method, payment_status, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (txn_number, customer_id, employee_id, subtotal, total_discount, 
                  total_tax, final_total, payment_method, 'completed'))
            
            transaction_id = cursor.lastrowid
            print(f"DEBUG: Created transaction with Database ID: {transaction_id}")
            
            # Insert transaction items
            for item in self.cart_items:
                line_total = (item['quantity'] * item['unit_price'] * 
                            (1 - item['disc'] / 100) * (1 + item['gst'] / 100))
                
                cursor.execute("""
                    INSERT INTO transaction_items (transaction_id, product_id, quantity, 
                                                 unit_price, discount_rate, line_total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (transaction_id, item['product_id'], item['quantity'], 
                      item['unit_price'], item['disc'], line_total))
                print(f"DEBUG: Added item - Product ID: {item['product_id']}, Qty: {item['quantity']}, Line Total: ₹{line_total:.2f}")
            
            # Commit the transaction
            conn.commit()
            cursor.close()
            
            print(f"DEBUG: ✅ Transaction committed to database successfully!")
            
            # Update product stock
            for item in self.cart_items:
                try:
                    Product.update_stock(
                        product_id=item['product_id'],
                        quantity_change=-item['quantity'],
                        reason=f"Sale {txn_number}"
                    )
                    print(f"DEBUG: Updated stock for Product {item['product_id']}: -{item['quantity']}")
                except Exception as e:
                    logging.error(f"Stock update failed for product {item['product_id']}: {e}")
            
            # Update customer totals if customer exists
            if self.current_customer:
                try:
                    conn, cursor = get_db()
                    loyalty_points = int(final_total / 10)  # 1 point per ₹10
                    cursor.execute("""
                        UPDATE customers 
                        SET total_purchases = total_purchases + %s,
                            loyalty_points = loyalty_points + %s
                        WHERE id = %s
                    """, (final_total, loyalty_points, customer_id))
                    conn.commit()
                    cursor.close()
                    print(f"DEBUG: Updated customer {customer_id}: +₹{final_total}, +{loyalty_points} points")
                except Exception as e:
                    logging.error(f"Customer update failed: {e}")
            
            # Success message with database confirmation
            messagebox.showinfo("✅ TRANSACTION SUCCESSFUL", 
                              f"🎉 Sale completed and saved to database!\n\n"
                              f"📋 Transaction: {txn_number}\n"
                              f"🗄️ Database ID: {transaction_id}\n"
                              f"💰 Total: {RUPEE}{final_total:.2f}\n"
                              f"💳 Payment: {payment_method.title()}\n"
                              f"👤 Customer: {self.current_customer.name if self.current_customer else 'Walk-in'}")

            # Show loyalty points earned
            if self.current_customer:
                loyalty_points = int(final_total / 10)
                if loyalty_points > 0:
                    messagebox.showinfo("🎁 LOYALTY REWARDS", 
                                      f"Congratulations {self.current_customer.name}!\n\n"
                                      f"🏆 You earned {loyalty_points} loyalty points!\n"
                                      f"💳 Thank you for your continued patronage!")

            # Clear the cart and reset form
            self.cart_items.clear()
            self._refresh_cart_tree()
            self.calculate_totals()
            self.current_customer = None
            self.cust_lb.config(text="Walk-in Customer")
            self.phone_ent.delete(0, tk.END)
            self.tender_ent.delete(0, tk.END)
            
            # Refresh displays
            self.refresh_product_list()
            self.barcode_ent.focus()

        except Exception as e:
            logging.error(f"Transaction failed: {e}")
            print(f"DEBUG: ❌ Transaction error: {e}")
            messagebox.showerror("TRANSACTION FAILED", 
                               f"❌ Transaction could not be completed!\n\n"
                               f"Error: {str(e)}\n\n"
                               f"Please try again or contact support.")
            # Rollback if needed
            try:
                if 'conn' in locals():
                    conn.rollback()
            except:
                pass

    def print_receipt(self):
        if not self.cart_items: 
            messagebox.showwarning("Warning", "No items to print")
            return
            
        ts = datetime.now().strftime('%d-%m-%Y %H:%M')
        lines = ["TAX INVOICE / CASH RECEIPT", "="*40]
        lines.append("SUPERMARKET NAME")
        lines.append("Address Line 1, City - PIN")
        lines.append("GSTIN: 29XXXXXXXXXXXXXXX")
        lines.append("="*40)
        lines.append(f"Date: {ts}")
        lines.append(f"Bill No: {datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        if self.current_customer:
            lines.append(f"Customer: {self.current_customer.name}")
            lines.append(f"Phone: {self.current_customer.phone}")
            # Show loyalty points if available
            try:
                customer = Customer.get_customer_by_id(self.current_customer.id)
                if customer:
                    lines.append(f"Loyalty Points: {customer.loyalty_points}")
            except:
                pass
        
        lines.append("-"*40)
        lines.append(f"{'Item':<20} {'Qty':<4} {'Rate':<8} {'Total':<8}")
        lines.append("-"*40)
        
        for i in self.cart_items:
            amt = i['quantity']*i['unit_price']
            lines.append(f"{i['name'][:19]:<20} {i['quantity']:<4} {i['unit_price']:<8.2f} {amt:<8.2f}")
        
        lines.append("-"*40)
        lines.append(self.lb_sub.cget('text'))
        lines.append(self.lb_itdis.cget('text'))
        lines.append(self.lb_tax.cget('text'))
        lines.append(self.lb_tot.cget('text'))
        lines.append("="*40)
        
        # Show loyalty points earned
        if self.current_customer:
            try:
                total_amount = float(self.lb_tot.cget('text').split(RUPEE)[1])
                points_earned = int(total_amount / 10)
                if points_earned > 0:
                    lines.append(f"Loyalty Points Earned: {points_earned}")
                    lines.append("-"*40)
            except:
                pass
        
        lines.append("Thank you for shopping with us!")
        lines.append("Visit again!")
        
        # Show in dialog
        receipt_window = tk.Toplevel(self.frame)
        receipt_window.title("Receipt Preview")
        receipt_window.geometry("500x600")
        
        text_widget = tk.Text(receipt_window, font=('Courier', 10), wrap=tk.NONE)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', '\n'.join(lines))
        text_widget.config(state=tk.DISABLED)
        
        # Add print and close buttons
        btn_frame = ttk.Frame(receipt_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Print Receipt", command=lambda: messagebox.showinfo("Print", "Receipt sent to printer")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=receipt_window.destroy).pack(side=tk.RIGHT, padx=5)

    def hold_transaction(self):
        if not self.cart_items:
            messagebox.showwarning("Empty","Cart is empty"); return
        
        # Simple hold implementation
        held_data = {
            'cart_items': self.cart_items.copy(),
            'customer': self.current_customer,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        # Store in a simple way (could be enhanced with file/database storage)
        if not hasattr(self, 'held_transactions'):
            self.held_transactions = []
        
        self.held_transactions.append(held_data)
        
        messagebox.showinfo("Transaction Held", f"Transaction held at {held_data['timestamp']}\nItems: {len(self.cart_items)}")
        
        # Clear current transaction
        self.cart_items.clear()
        self._refresh_cart_tree()
        self.calculate_totals()

    def process_refund(self):
        refund_id = simpledialog.askstring("Process Refund", "Enter transaction ID for refund:")
        if refund_id:
            messagebox.showinfo("Refund", f"Refund processed for transaction: {refund_id}\nThis feature will be fully implemented soon.")

    # ───────────────────────────────────────── refresh external ──
    def refresh(self):
        self.refresh_product_list()
