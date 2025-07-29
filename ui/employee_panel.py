"""
Employee management interface
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.employee import Employee
from datetime import datetime
import logging


class EmployeePanel:
    def __init__(self, notebook, main_app):
        self.notebook = notebook
        self.main_app = main_app
        self.create_employee_interface()

    def create_employee_interface(self):
        """Create employee management interface"""
        self.frame = ttk.Frame(self.notebook, padding=10)
        
        # Create paned window layout
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Employee form
        left_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Employee list
        right_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(right_frame, weight=2)
        
        self.create_employee_form(left_frame)
        self.create_employee_list(right_frame)
        self.create_hr_tools(left_frame)
        
        # Load initial data
        self.refresh_employee_list()

    def create_employee_form(self, parent):
        """Create employee input form with hire date field"""
        form_frame = ttk.LabelFrame(parent, text="Employee Information", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Employee ID
        ttk.Label(form_frame, text="Employee ID:").grid(row=0, column=0, sticky='w', pady=3)
        self.employee_id_entry = ttk.Entry(form_frame, width=25)
        self.employee_id_entry.grid(row=0, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Full name
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, sticky='w', pady=3)
        self.name_entry = ttk.Entry(form_frame, width=25)
        self.name_entry.grid(row=1, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Phone number
        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky='w', pady=3)
        self.phone_entry = ttk.Entry(form_frame, width=25)
        self.phone_entry.grid(row=2, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky='w', pady=3)
        self.email_entry = ttk.Entry(form_frame, width=25)
        self.email_entry.grid(row=3, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Address
        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky='w', pady=3)
        self.address_text = tk.Text(form_frame, height=3, width=25)
        self.address_text.grid(row=4, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Position
        ttk.Label(form_frame, text="Position:").grid(row=5, column=0, sticky='w', pady=3)
        self.position_combo = ttk.Combobox(form_frame, values=[
            'Manager', 'Cashier', 'Stock Clerk', 'Supervisor', 'Security', 'Cleaner', 'Delivery', 'Assistant Manager'
        ], width=22, state="readonly")
        self.position_combo.grid(row=5, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Department
        ttk.Label(form_frame, text="Department:").grid(row=6, column=0, sticky='w', pady=3)
        self.department_combo = ttk.Combobox(form_frame, values=[
            'Sales', 'Inventory', 'Customer Service', 'Administration', 'Security', 'Maintenance'
        ], width=22, state="readonly")
        self.department_combo.grid(row=6, column=1, sticky='ew', pady=3, padx=(5, 0))
        
        # Salary (in Indian Rupees)
        ttk.Label(form_frame, text="Salary (₹):").grid(row=7, column=0, sticky='w', pady=3)
        self.salary_entry = ttk.Entry(form_frame, width=25)
        self.salary_entry.grid(row=7, column=1, sticky='ew', pady=3, padx=(5, 0))
        

        ttk.Label(form_frame, text="Hire Date (DD-MM-YYYY):").grid(row=8, column=0, sticky='w', pady=3)
        self.hire_date_entry = ttk.Entry(form_frame, width=25)
        self.hire_date_entry.grid(row=8, column=1, sticky='ew', pady=3, padx=(5, 0))
        # Set placeholder text
        self.hire_date_entry.insert(0, datetime.now().strftime('%d-%m-%Y'))
        
        # Action buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Add Employee", command=self.add_employee).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Update Employee", command=self.update_employee).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete Employee", command=self.delete_employee).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=2)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

    def create_employee_list(self, parent):
        """Create employee list with search"""
        # Search section
        search_frame = ttk.LabelFrame(parent, text="Search Employees", padding=5)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_controls = ttk.Frame(search_frame)
        search_controls.pack(fill=tk.X)
        
        ttk.Label(search_controls, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_controls, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Label(search_controls, text="Department:").pack(side=tk.LEFT)
        self.filter_department = ttk.Combobox(search_controls, values=[
            'All', 'Sales', 'Inventory', 'Customer Service', 'Administration', 'Security', 'Maintenance'
        ], width=15, state="readonly")
        self.filter_department.set('All')
        self.filter_department.pack(side=tk.LEFT, padx=(5, 10))
        self.filter_department.bind('<<ComboboxSelected>>', self.apply_department_filter)
        
        ttk.Button(search_controls, text="Search", command=self.search_employees).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_controls, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_controls, text="Refresh", command=self.refresh_employee_list).pack(side=tk.LEFT, padx=2)
        
        # Employee list
        list_frame = ttk.LabelFrame(parent, text="Employee Database", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Employee ID', 'Name', 'Position', 'Department', 'Phone', 'Salary (₹)', 'Hire Date', 'Status')
        self.employee_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.employee_tree.heading(col, text=col)
            if col == 'Name':
                self.employee_tree.column(col, width=150)
            elif col == 'Salary (₹)':
                self.employee_tree.column(col, width=100, anchor='e')
            elif col == 'Phone':
                self.employee_tree.column(col, width=120)
            else:
                self.employee_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.employee_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.employee_tree.xview)
        self.employee_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.employee_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)
        self.employee_tree.bind('<Double-1>', self.on_employee_double_click)

    def create_hr_tools(self, parent):
        """Create HR management tools"""
        hr_frame = ttk.LabelFrame(parent, text="HR Tools", padding=10)
        hr_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Attendance tracking
        attendance_frame = ttk.Frame(hr_frame)
        attendance_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(attendance_frame, text="Attendance:").pack(anchor='w')
        attendance_buttons = ttk.Frame(attendance_frame)
        attendance_buttons.pack(fill=tk.X, pady=2)
        
        ttk.Button(attendance_buttons, text="Clock In", command=self.clock_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(attendance_buttons, text="Clock Out", command=self.clock_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(attendance_buttons, text="View Timesheet", command=self.view_timesheet).pack(side=tk.LEFT, padx=2)
        
        # Reports
        reports_frame = ttk.Frame(hr_frame)
        reports_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(reports_frame, text="Reports:").pack(anchor='w')
        report_buttons = ttk.Frame(reports_frame)
        report_buttons.pack(fill=tk.X, pady=2)
        
        ttk.Button(report_buttons, text="Employee Report", command=self.generate_employee_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(report_buttons, text="Payroll Summary", command=self.payroll_summary).pack(side=tk.LEFT, padx=2)

    def add_employee(self):
        """Add new employee with hire date validation"""
        try:
            employee_id = self.employee_id_entry.get().strip()
            name = self.name_entry.get().strip()
            phone = self.phone_entry.get().strip()
            email = self.email_entry.get().strip()
            address = self.address_text.get('1.0', tk.END).strip()
            position = self.position_combo.get().strip()
            department = self.department_combo.get().strip()
            salary = self.salary_entry.get().strip()
            hire_date = self.hire_date_entry.get().strip()
            
            if not employee_id or not name:
                messagebox.showerror("Error", "Employee ID and name are required")
                return
            
            try:
                salary_float = float(salary) if salary else 0.0
            except ValueError:
                messagebox.showerror("Error", "Invalid salary amount")
                return
            
            # Validate and format hire date
            hire_date_formatted = None
            if hire_date:
                try:
                    # Try DD-MM-YYYY format first
                    hire_date_obj = datetime.strptime(hire_date, '%d-%m-%Y')
                    hire_date_formatted = hire_date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        # Try YYYY-MM-DD format
                        hire_date_obj = datetime.strptime(hire_date, '%Y-%m-%d')
                        hire_date_formatted = hire_date
                    except ValueError:
                        messagebox.showerror("Error", "Invalid date format. Please use DD-MM-YYYY")
                        return
            
            Employee.create_employee(
                employee_id=employee_id,
                name=name,
                phone=phone if phone else None,
                email=email if email else None,
                address=address if address else None,
                position=position if position else None,
                salary=salary_float,
                department=department if department else None,
                hire_date=hire_date_formatted
            )
            
            messagebox.showinfo("Success", "Employee added successfully")
            self.clear_form()
            self.refresh_employee_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add employee: {str(e)}")
            logging.error(f"Error adding employee: {e}")

    def update_employee(self):
        """Update selected employee"""
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee to update")
            return
        
        try:
            item = self.employee_tree.item(selection[0])
            employee_id = item['values'][1]  # Employee ID, not database ID
            
            update_data = {}
            
            name = self.name_entry.get().strip()
            if name: update_data['name'] = name
            
            phone = self.phone_entry.get().strip()
            if phone: update_data['phone'] = phone
            
            email = self.email_entry.get().strip()
            if email: update_data['email'] = email
            
            address = self.address_text.get('1.0', tk.END).strip()
            if address: update_data['address'] = address
            
            position = self.position_combo.get().strip()
            if position: update_data['position'] = position
            
            department = self.department_combo.get().strip()
            if department: update_data['department'] = department
            
            salary = self.salary_entry.get().strip()
            if salary:
                try:
                    update_data['salary'] = float(salary)
                except ValueError:
                    messagebox.showerror("Error", "Invalid salary amount")
                    return
            
            if update_data:
                Employee.update_employee(employee_id, **update_data)
                messagebox.showinfo("Success", "Employee updated successfully")
                self.refresh_employee_list()
            else:
                messagebox.showwarning("Warning", "No data to update")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update employee: {str(e)}")

    def delete_employee(self):
        """Delete selected employee"""
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee to delete")
            return
        
        item = self.employee_tree.item(selection[0])
        employee_name = item['values'][2]
        
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete '{employee_name}'?"):
            return
        
        try:
            employee_id = item['values'][1]
            
            Employee.delete_employee(employee_id)
            
            messagebox.showinfo("Success", "Employee deleted successfully")
            self.clear_form()
            self.refresh_employee_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete employee: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        self.employee_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_text.delete('1.0', tk.END)
        self.position_combo.set('')
        self.department_combo.set('')
        self.salary_entry.delete(0, tk.END)
        self.hire_date_entry.delete(0, tk.END)
        # Set default hire date to today
        self.hire_date_entry.insert(0, datetime.now().strftime('%d-%m-%Y'))

    def refresh_employee_list(self):
        """Refresh employee list with Indian currency format"""
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        try:
            employees = Employee.get_all()
            for employee in employees:
                status = "Active" if employee.is_active else "Inactive"
                

                hire_date = 'N/A'
                if employee.hire_date:
                    try:
                        if isinstance(employee.hire_date, str):
                            date_obj = datetime.strptime(employee.hire_date, '%Y-%m-%d').date()
                            hire_date = date_obj.strftime('%d-%m-%Y')
                        else:
                            hire_date = employee.hire_date.strftime('%d-%m-%Y')
                    except:
                        hire_date = str(employee.hire_date)
                

                salary_display = f"₹{employee.salary:,.2f}" if employee.salary else "₹0.00"
                
                self.employee_tree.insert('', tk.END, values=(
                    employee.id,
                    employee.employee_id,
                    employee.name,
                    employee.position or '',
                    employee.department or '',
                    employee.phone or '',
                    salary_display,
                    hire_date,
                    status
                ))
        except Exception as e:
            logging.error(f"Error refreshing employee list: {e}")

    def on_search_change(self, event=None):
        """Handle real-time search"""
        search_term = self.search_entry.get().strip()
        if len(search_term) >= 2:
            self.search_employees()
        elif len(search_term) == 0:
            self.refresh_employee_list()

    def search_employees(self):
        """Search employees"""
        search_term = self.search_entry.get().strip()
        
        try:
            if search_term:
                employees = Employee.search_employees(search_term)
            else:
                employees = Employee.get_all()
            
            # Clear current list
            for item in self.employee_tree.get_children():
                self.employee_tree.delete(item)
            
            # Apply department filter if selected
            department_filter = self.filter_department.get()
            if department_filter != 'All':
                employees = [emp for emp in employees if emp.department == department_filter]
            
            # Populate with filtered results
            for employee in employees:
                status = "Active" if employee.is_active else "Inactive"
                
                hire_date = 'N/A'
                if employee.hire_date:
                    try:
                        if isinstance(employee.hire_date, str):
                            date_obj = datetime.strptime(employee.hire_date, '%Y-%m-%d').date()
                            hire_date = date_obj.strftime('%d-%m-%Y')
                        else:
                            hire_date = employee.hire_date.strftime('%d-%m-%Y')
                    except:
                        hire_date = str(employee.hire_date)
                
                salary_display = f"₹{employee.salary:,.2f}" if employee.salary else "₹0.00"
                
                self.employee_tree.insert('', tk.END, values=(
                    employee.id,
                    employee.employee_id,
                    employee.name,
                    employee.position or '',
                    employee.department or '',
                    employee.phone or '',
                    salary_display,
                    hire_date,
                    status
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def apply_department_filter(self, event=None):
        """Apply department filter"""
        self.search_employees()

    def clear_search(self):
        """Clear search and refresh full list"""
        self.search_entry.delete(0, tk.END)
        self.filter_department.set('All')
        self.refresh_employee_list()

    def on_employee_select(self, event):
        """Handle employee selection"""
        selection = self.employee_tree.selection()
        if selection:
            item = self.employee_tree.item(selection[0])
            employee_id = item['values'][1]
            
            # Load employee details into form
            try:
                employee = Employee.get_employee_by_id(employee_id)
                if employee:
                    self.load_employee_to_form(employee)
            except Exception as e:
                logging.error(f"Error loading employee details: {e}")

    def on_employee_double_click(self, event):
        """Handle double-click on employee"""
        self.view_timesheet()

    def load_employee_to_form(self, employee):
        """Load employee data into form"""
        self.clear_form()
        
        self.employee_id_entry.insert(0, employee.employee_id)
        self.name_entry.insert(0, employee.name)
        if employee.phone:
            self.phone_entry.insert(0, employee.phone)
        if employee.email:
            self.email_entry.insert(0, employee.email)
        if employee.address:
            self.address_text.insert('1.0', employee.address)
        if employee.position:
            self.position_combo.set(employee.position)
        if employee.department:
            self.department_combo.set(employee.department)
        if employee.salary:
            self.salary_entry.insert(0, str(employee.salary))
        

        if employee.hire_date:
            try:
                if isinstance(employee.hire_date, str):
                    date_obj = datetime.strptime(employee.hire_date, '%Y-%m-%d').date()
                    self.hire_date_entry.insert(0, date_obj.strftime('%d-%m-%Y'))
                else:
                    self.hire_date_entry.insert(0, employee.hire_date.strftime('%d-%m-%Y'))
            except:
                self.hire_date_entry.insert(0, str(employee.hire_date))

    def clock_in(self):
        """Clock in employee"""
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee")
            return
        
        item = self.employee_tree.item(selection[0])
        employee_name = item['values'][2]
        current_time = datetime.now().strftime('%H:%M:%S')
        
        messagebox.showinfo("Clock In", f"{employee_name} clocked in at {current_time}")

    def clock_out(self):
        """Clock out employee"""
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee")
            return
        
        item = self.employee_tree.item(selection[0])
        employee_name = item['values'][2]
        current_time = datetime.now().strftime('%H:%M:%S')
        
        messagebox.showinfo("Clock Out", f"{employee_name} clocked out at {current_time}")

    def view_timesheet(self):

        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee")
            return
        
        item = self.employee_tree.item(selection[0])
        employee_name = item['values'][2]
        employee_id = item['values'][1]
        
        # Create timesheet window
        timesheet_window = tk.Toplevel(self.frame)
        timesheet_window.title(f"Timesheet - {employee_name}")
        timesheet_window.geometry("950x700")
        timesheet_window.grab_set()
        
        # Header
        header_frame = ttk.Frame(timesheet_window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"Timesheet for {employee_name} (ID: {employee_id})", 
                 font=('Segoe UI', 14, 'bold')).pack()
        
        ttk.Label(header_frame, text=f"Period: {datetime.now().strftime('%B %Y')}", 
                 font=('Segoe UI', 10)).pack()
        
        # Timesheet data frame
        timesheet_frame = ttk.Frame(timesheet_window)
        timesheet_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ('Date', 'Day', 'Clock In', 'Clock Out', 'Hours', 'Overtime', 'Status')
        timesheet_tree = ttk.Treeview(timesheet_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            timesheet_tree.heading(col, text=col)
            if col == 'Date':
                timesheet_tree.column(col, width=100)
            elif col == 'Day':
                timesheet_tree.column(col, width=80)
            elif col in ['Clock In', 'Clock Out']:
                timesheet_tree.column(col, width=80)
            elif col in ['Hours', 'Overtime']:
                timesheet_tree.column(col, width=70, anchor='center')
            else:
                timesheet_tree.column(col, width=90)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(timesheet_frame, orient=tk.VERTICAL, command=timesheet_tree.yview)
        timesheet_tree.configure(yscrollcommand=scrollbar.set)
        
        timesheet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sample timesheet data (replace with actual data from database)
        import calendar
        today = datetime.now()
        current_month_days = calendar.monthrange(today.year, today.month)[1]
        
        total_hours = 0
        total_overtime = 0
        days_present = 0
        days_absent = 0
        
        for day in range(1, min(current_month_days + 1, today.day + 1)):
            date = datetime(today.year, today.month, day)
            day_name = date.strftime('%a')
            
            if day_name in ['Sat', 'Sun']:
                status = 'Weekend'
                clock_in = '--'
                clock_out = '--'
                hours = '0.0'
                overtime = '0.0'
            elif day <= today.day - 3:  # Past days
                if day % 7 == 0:  # Some random absence
                    status = 'Absent'
                    clock_in = '--'
                    clock_out = '--'
                    hours = '0.0'
                    overtime = '0.0'
                    days_absent += 1
                else:
                    status = 'Present'
                    clock_in = '09:00'
                    clock_out = '17:30'
                    hours = '8.5'
                    overtime = '0.5' if day % 5 == 0 else '0.0'
                    total_hours += 8.5
                    total_overtime += float(overtime)
                    days_present += 1
            else:
                status = 'Future'
                clock_in = '--'
                clock_out = '--'
                hours = '0.0'
                overtime = '0.0'
            
            timesheet_tree.insert('', tk.END, values=(
                date.strftime('%d-%m-%Y'),
                day_name,
                clock_in,
                clock_out,
                hours,
                overtime,
                status
            ))
        

        summary_frame = ttk.LabelFrame(timesheet_window, text="Monthly Summary", padding=15)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a text widget for better summary display
        summary_text_widget = tk.Text(summary_frame, height=8, wrap=tk.WORD, 
                                     font=('Segoe UI', 10), bg='#f0f0f0', 
                                     state=tk.NORMAL, relief=tk.FLAT)
        summary_text_widget.pack(fill=tk.X, padx=5, pady=5)
        
        working_days = days_present + days_absent
        attendance_rate = (days_present / working_days * 100) if working_days > 0 else 0
        avg_hours = (total_hours / days_present) if days_present > 0 else 0
        
        summary_content = f"""MONTHLY ATTENDANCE SUMMARY FOR {employee_name}
{'='*60}

📅 Total Working Days (excluding weekends): {working_days}
✅ Days Present: {days_present}
❌ Days Absent: {days_absent}
⏰ Total Hours Worked: {total_hours:.1f} hours
⏱️  Total Overtime Hours: {total_overtime:.1f} hours
📊 Average Hours/Day: {avg_hours:.1f} hours
📈 Attendance Rate: {attendance_rate:.1f}%

💰 Monthly Performance:
   • Regular Hours: {total_hours - total_overtime:.1f} hours
   • Overtime Hours: {total_overtime:.1f} hours
   • Total Productive Hours: {total_hours:.1f} hours"""

        summary_text_widget.insert('1.0', summary_content)
        summary_text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_frame = ttk.Frame(timesheet_window)
        close_frame.pack(pady=10)
        ttk.Button(close_frame, text="Close", command=timesheet_window.destroy, width=15).pack()

    def generate_employee_report(self):
        """Generate comprehensive employee report"""
        try:
            employees = Employee.get_all()
            
            # Create report window
            report_window = tk.Toplevel(self.frame)
            report_window.title("Employee Report")
            report_window.geometry("800x600")
            
            # Report text
            report_frame = ttk.Frame(report_window)
            report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            report_text = tk.Text(report_frame, wrap=tk.WORD, font=('Courier', 10))
            scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=report_text.yview)
            report_text.configure(yscrollcommand=scrollbar.set)
            
            # Generate report content
            report_content = f"EMPLOYEE REPORT - {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
            report_content += "=" * 80 + "\n\n"
            
            active_employees = [emp for emp in employees if emp.is_active]
            report_content += f"Total Employees: {len(employees)}\n"
            report_content += f"Active Employees: {len(active_employees)}\n"
            report_content += f"Inactive Employees: {len(employees) - len(active_employees)}\n\n"
            
            # Department breakdown
            departments = {}
            for emp in active_employees:
                dept = emp.department or 'Unassigned'
                departments[dept] = departments.get(dept, 0) + 1
            
            report_content += "DEPARTMENT BREAKDOWN:\n"
            report_content += "-" * 40 + "\n"
            for dept, count in sorted(departments.items()):
                report_content += f"{dept:.<30} {count:>3} employees\n"
            
            # Position breakdown
            positions = {}
            for emp in active_employees:
                pos = emp.position or 'Unassigned'
                positions[pos] = positions.get(pos, 0) + 1
            
            report_content += "\nPOSITION BREAKDOWN:\n"
            report_content += "-" * 40 + "\n"
            for pos, count in sorted(positions.items()):
                report_content += f"{pos:.<30} {count:>3} employees\n"
            
            # Salary statistics
            salaries = [emp.salary for emp in active_employees if emp.salary]
            if salaries:
                avg_salary = sum(salaries) / len(salaries)
                min_salary = min(salaries)
                max_salary = max(salaries)
                
                report_content += "\nSALARY STATISTICS:\n"
                report_content += "-" * 40 + "\n"
                report_content += f"Average Salary: ₹{avg_salary:,.2f}\n"
                report_content += f"Minimum Salary: ₹{min_salary:,.2f}\n"
                report_content += f"Maximum Salary: ₹{max_salary:,.2f}\n"
                report_content += f"Total Payroll: ₹{sum(salaries):,.2f}\n"
            
            report_content += "\nDETAILED EMPLOYEE LIST:\n"
            report_content += "=" * 80 + "\n"
            report_content += f"{'EMP ID':<8} {'NAME':<20} {'POSITION':<15} {'DEPARTMENT':<15} {'SALARY':<12} {'STATUS'}\n"
            report_content += "-" * 80 + "\n"
            
            for emp in sorted(employees, key=lambda x: x.employee_id):
                status = "Active" if emp.is_active else "Inactive"
                salary_str = f"₹{emp.salary:,.0f}" if emp.salary else "N/A"
                report_content += f"{emp.employee_id:<8} {emp.name[:19]:<20} {(emp.position or 'N/A')[:14]:<15} {(emp.department or 'N/A')[:14]:<15} {salary_str:<12} {status}\n"
            
            report_text.insert('1.0', report_content)
            report_text.config(state=tk.DISABLED)
            
            report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Print button
            ttk.Button(report_window, text="Print Report", 
                      command=lambda: messagebox.showinfo("Print", "Report sent to printer")).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def payroll_summary(self):
       
        try:
            employees = Employee.get_all()
            active_employees = [emp for emp in employees if emp.is_active]
            
            total_payroll = sum(emp.salary or 0 for emp in active_employees)
            average_salary = total_payroll / len(active_employees) if active_employees else 0
            
            # Create payroll window - increased size
            payroll_window = tk.Toplevel(self.frame)
            payroll_window.title("Payroll Summary")
            payroll_window.geometry("700x600")
            
            # Header
            header_label = ttk.Label(payroll_window, text="PAYROLL SUMMARY", 
                                   font=('Segoe UI', 16, 'bold'))
            header_label.pack(pady=20)
            
            # Summary stats
            stats_frame = ttk.LabelFrame(payroll_window, text="Overview", padding=20)
            stats_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Label(stats_frame, text=f"Active Employees: {len(active_employees)}", 
                     font=('Segoe UI', 12)).pack(anchor='w', pady=5)
            ttk.Label(stats_frame, text=f"Total Monthly Payroll: ₹{total_payroll:,.2f}", 
                     font=('Segoe UI', 12, 'bold'), foreground='green').pack(anchor='w', pady=5)
            ttk.Label(stats_frame, text=f"Average Salary: ₹{average_salary:,.2f}", 
                     font=('Segoe UI', 12)).pack(anchor='w', pady=5)
            ttk.Label(stats_frame, text=f"Annual Payroll: ₹{total_payroll * 12:,.2f}", 
                     font=('Segoe UI', 12)).pack(anchor='w', pady=5)
            

            dept_frame = ttk.LabelFrame(payroll_window, text="Department-wise Payroll", padding=15)
            dept_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Create frame for treeview and scrollbar
            tree_frame = ttk.Frame(dept_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            

            dept_columns = ('Department', 'Count', 'Monthly Payroll', 'Avg Salary')
            dept_tree = ttk.Treeview(tree_frame, columns=dept_columns, show='headings', height=8)
            

            dept_tree.column('Department', width=150, minwidth=120, anchor='w')
            dept_tree.column('Count', width=80, minwidth=60, anchor='center')
            dept_tree.column('Monthly Payroll', width=150, minwidth=120, anchor='e')
            dept_tree.column('Avg Salary', width=150, minwidth=120, anchor='e')
            
            # Set proper headings
            dept_tree.heading('Department', text='Department')
            dept_tree.heading('Count', text='Employees')
            dept_tree.heading('Monthly Payroll', text='Monthly Payroll (₹)')
            dept_tree.heading('Avg Salary', text='Average Salary (₹)')
            
            # Add scrollbar
            dept_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=dept_tree.yview)
            dept_tree.configure(yscrollcommand=dept_scrollbar.set)
            
            # Pack treeview and scrollbar
            dept_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            dept_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Calculate department-wise data
            dept_data = {}
            for emp in active_employees:
                dept = emp.department or 'Unassigned'
                if dept not in dept_data:
                    dept_data[dept] = {'count': 0, 'total': 0}
                dept_data[dept]['count'] += 1
                dept_data[dept]['total'] += emp.salary or 0
            
            # Populate treeview with department data
            for dept, data in sorted(dept_data.items()):
                avg = data['total'] / data['count'] if data['count'] > 0 else 0
                dept_tree.insert('', tk.END, values=(
                    dept,
                    f"{data['count']}",
                    f"₹{data['total']:,.0f}",
                    f"₹{avg:,.0f}"
                ))
            
            # Close button
            close_frame = ttk.Frame(payroll_window)
            close_frame.pack(pady=15)
            ttk.Button(close_frame, text="Close", command=payroll_window.destroy, width=15).pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate payroll summary: {str(e)}")

    def refresh(self):
        """Refresh panel data"""
        self.refresh_employee_list()
