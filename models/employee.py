"""
Employee management model
"""
from database import get_db
from datetime import datetime
import logging
import hashlib
import os


class Employee:
    def __init__(self, id=None, employee_code=None, name=None, email=None, phone=None, 
                 role=None, password_hash=None, salary=None, hire_date=None, 
                 status='active', last_login=None, created_at=None, updated_at=None,
                 department=None):  # Add department parameter
        
        self.id = id
        self.employee_code = employee_code
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role
        self.password_hash = password_hash
        self.salary = salary
        self.hire_date = hire_date
        self.status = status  # Using 'status' field from database schema
        self.last_login = last_login
        self.created_at = created_at
        self.updated_at = updated_at
        self.employee_id = employee_code  # UI compatibility
        self.is_active = (status == 'active')  # UI compatibility
        
        #  Map position from role properly
        position_mapping = {
            'manager': 'Manager',
            'cashier': 'Cashier',
            'stock clerk': 'Stock Clerk',
            'supervisor': 'Supervisor',
            'security': 'Security',
            'cleaner': 'Cleaner',
            'delivery': 'Delivery',
            'assistant manager': 'Assistant Manager',
            'admin': 'Manager',  # Show admin as Manager in UI
            'inventory_manager': 'Stock Clerk'
        }
        self.position = position_mapping.get(role.lower() if role else '', 'Cashier')
        
        if department:
            self.department = department
        else:
            department_mapping = {
                'manager': 'Administration',
                'cashier': 'Sales',
                'stock clerk': 'Inventory',
                'supervisor': 'Administration',
                'security': 'Security',
                'cleaner': 'Maintenance',
                'delivery': 'Sales',
                'assistant manager': 'Administration',
                'admin': 'Administration',
                'inventory_manager': 'Inventory'
            }
            self.department = department_mapping.get(role.lower() if role else '', 'Sales')
        
        self.address = ''  # Default address for UI compatibility

    @staticmethod
    def generate_employee_code():
        """Generate unique employee code - matches your EMP001 format"""
        try:
            conn, cursor = get_db()
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0]
            cursor.close()
            return f"EMP{count + 1:03d}"  # EMP001, EMP002, etc.
        except Exception as e:
            logging.error(f"Error generating employee code: {e}")
            return f"EMP{datetime.now().strftime('%H%M%S')}"

    @classmethod
    def create_employee(cls, name, email=None, phone=None, role='cashier', **kwargs):
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Creating employee: {name}")
            print(f"🔍 DEBUG: Received parameters - email: {email}, phone: {phone}, role: {role}")
            print(f"🔍 DEBUG: Received kwargs: {kwargs}")
            
            conn, cursor = get_db()
            
            # Auto-generate employee_code if not provided
            employee_code = kwargs.get('employee_code')
            if not employee_code:
                employee_code = cls.generate_employee_code()
                print(f"🔍 DEBUG: Generated employee_code: {employee_code}")
            
            # Check if employee_code already exists
            cursor.execute("SELECT id FROM employees WHERE employee_code = %s", (employee_code,))
            if cursor.fetchone():
                raise ValueError("Employee code already exists")
            
            # Handle password hashing
            password = kwargs.get('password', 'default123')
            salt = os.urandom(16).hex()
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            actual_role = role
            if 'position' in kwargs and kwargs['position']:
                actual_role = kwargs['position'].lower()
                print(f"🔍 DEBUG: Using position from kwargs: {kwargs['position']} -> {actual_role}")
            elif 'role' in kwargs and kwargs['role']:
                actual_role = kwargs['role'].lower()
                print(f"🔍 DEBUG: Using role from kwargs: {kwargs['role']} -> {actual_role}")
            
            department = kwargs.get('department', 'Sales')
            print(f"🔍 DEBUG: Department from UI: {department}")
            
            # Handle employee_id field from UI (alternative name for employee_code)
            if 'employee_id' in kwargs and kwargs['employee_id'] and not employee_code:
                employee_code = kwargs['employee_id']
                print(f"🔍 DEBUG: Using employee_id from kwargs: {employee_code}")
            
            # Handle hire_date formatting
            hire_date = kwargs.get('hire_date')
            if hire_date and isinstance(hire_date, str):
                try:
                    if '-' in hire_date and len(hire_date.split('-')[0]) == 2:  # DD-MM-YYYY
                        hire_date_obj = datetime.strptime(hire_date, '%d-%m-%Y')
                        hire_date = hire_date_obj.strftime('%Y-%m-%d')
                        print(f"🔍 DEBUG: Converted hire_date: {kwargs['hire_date']} -> {hire_date}")
                except ValueError:
                    hire_date = datetime.now().date()
                    print(f"🔍 DEBUG: Invalid hire_date format, using current date: {hire_date}")
            elif not hire_date:
                hire_date = datetime.now().date()
                print(f"🔍 DEBUG: No hire_date provided, using current date: {hire_date}")
            
            print(f"🔍 DEBUG: Final parameters for database:")
            print(f"   - employee_code: {employee_code}")
            print(f"   - name: {name}")
            print(f"   - email: {email}")
            print(f"   - phone: {phone}")
            print(f"   - role: {actual_role}")
            print(f"   - department: {department}")
            print(f"   - salary: {kwargs.get('salary')}")
            print(f"   - hire_date: {hire_date}")
            
            try:
                cursor.execute("""
                    INSERT INTO employees (
                        employee_code, name, email, phone, role, department, password_hash, 
                        salary, hire_date, status
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    employee_code, 
                    name, 
                    email, 
                    phone, 
                    actual_role,
                    department,  # Store department in database
                    password_hash,
                    kwargs.get('salary'), 
                    hire_date, 
                    kwargs.get('status', 'active')
                ))
                print(f"🔍 DEBUG: Used INSERT with department column")
            except Exception as db_error:
                print(f"🔍 DEBUG: Department column doesn't exist, using INSERT without department")
                cursor.execute("""
                    INSERT INTO employees (
                        employee_code, name, email, phone, role, password_hash, 
                        salary, hire_date, status
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    employee_code, 
                    name, 
                    email, 
                    phone, 
                    actual_role,  # Use the processed role
                    password_hash,
                    kwargs.get('salary'), 
                    hire_date, 
                    kwargs.get('status', 'active')
                ))
            
            employee_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ DEBUG: Employee created with ID: {employee_id}")
            print(f"✅ DEBUG: Employee stored with role: {actual_role}, department: {department}")
            logging.info(f"Employee created successfully: {name} (Code: {employee_code}, Role: {actual_role})")
            return employee_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error creating employee: {e}")
            logging.error(f"Error creating employee: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def add_employee(cls, name, **kwargs):
        """Alternative method for backward compatibility"""
        print(f"🔍 DEBUG: add_employee called with name: {name}, kwargs: {kwargs}")
        return cls.create_employee(
            name=name,
            email=kwargs.get('email'),
            phone=kwargs.get('phone'),
            role=kwargs.get('role', kwargs.get('position', 'cashier')),  #  role and position
            **kwargs
        )

    @classmethod
    def get_all_employees(cls):
        try:
            print("🔍 DEBUG: Fetching all employees...")
            
            conn, cursor = get_db()
            
            # First, test basic connectivity
            cursor.execute("SELECT COUNT(*) FROM employees")
            total_count = cursor.fetchone()[0]
            print(f"🔍 DEBUG: Total employees in database: {total_count}")
            
            # Test active employees count
            cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            print(f"🔍 DEBUG: Active employees in database: {active_count}")
            
            # Try to fetch with department column first
            try:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, department, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE status = 'active'
                    ORDER BY employee_code
                """)
                has_department_column = True
                print(f"🔍 DEBUG: Using query with department column")
            except Exception as e:
                print(f"🔍 DEBUG: Department column doesn't exist, using query without department")
                # Fetch without department column
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE status = 'active'
                    ORDER BY employee_code
                """)
                has_department_column = False
            
            employees_data = cursor.fetchall()
            print(f"🔍 DEBUG: Raw employee data fetched: {len(employees_data)} records")
            
            if employees_data:
                print(f"🔍 DEBUG: First employee raw data: {employees_data[0]}")
            
            cursor.close()
            
            employees = []
            for i, data in enumerate(employees_data):
                try:
                    print(f"🔍 DEBUG: Processing employee {i+1}: {data[1]} - {data[2]}")  # code, name
                    
                    if has_department_column:
                        # Create employee object with department field
                        employee = cls(
                            id=data[0],
                            employee_code=data[1], 
                            name=data[2],
                            email=data[3], 
                            phone=data[4],
                            role=data[5],
                            department=data[6],  # Department from database
                            password_hash=data[7],
                            salary=data[8],
                            hire_date=data[9],
                            status=data[10],
                            last_login=data[11],
                            created_at=data[12],
                            updated_at=data[13]
                        )
                    else:
                        # Create employee object without department field (will be mapped from role)
                        employee = cls(
                            id=data[0],
                            employee_code=data[1], 
                            name=data[2],
                            email=data[3], 
                            phone=data[4],
                            role=data[5],
                            password_hash=data[6],
                            salary=data[7],
                            hire_date=data[8],
                            status=data[9],
                            last_login=data[10],
                            created_at=data[11],
                            updated_at=data[12]
                        )
                    
                    print(f"🔍 DEBUG: Employee {i+1} - Role: {employee.role}, Department: {employee.department}")
                    employees.append(employee)
                    
                except Exception as e:
                    print(f"❌ DEBUG: Error processing employee {i+1}: {e}")
                    print(f"❌ DEBUG: Data causing error: {data}")
                    continue
            
            print(f"✅ DEBUG: Successfully processed {len(employees)} employees")
            return employees
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting employees: {e}")
            logging.error(f"Error getting employees: {e}")
            import traceback
            traceback.print_exc()
            return []

    @classmethod
    def get_all(cls):
        """Alias for compatibility with UI"""
        return cls.get_all_employees()

    @classmethod
    def get_all_employees_simple(cls):
        """Simple employee fetch for testing"""
        try:
            print("🔍 DEBUG: Fetching employees with simple query...")
            
            conn, cursor = get_db()
            
            cursor.execute("""
                SELECT employee_code, name, email, phone, role, status
                FROM employees
                WHERE status = 'active'
                ORDER BY employee_code
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            print(f"✅ DEBUG: Simple fetch returned {len(results)} employees")
            for result in results:
                print(f"   - {result[0]}: {result[1]} ({result[4]}) - {result[5]}")
            
            return results
            
        except Exception as e:
            print(f"❌ DEBUG: Simple fetch failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    @classmethod
    def search_employees(cls, search_term):
        """Search employees - MATCHES YOUR SCHEMA"""
        try:
            print(f"🔍 DEBUG: Searching employees for: {search_term}")
            
            conn, cursor = get_db()
            search_pattern = f"%{search_term}%"
            
            # Try with department column first
            try:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, department, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE (name LIKE %s OR employee_code LIKE %s OR email LIKE %s OR 
                           phone LIKE %s OR role LIKE %s)
                          AND status = 'active'
                    ORDER BY name
                """, (search_pattern, search_pattern, search_pattern, 
                      search_pattern, search_pattern))
                has_department = True
            except:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE (name LIKE %s OR employee_code LIKE %s OR email LIKE %s OR 
                           phone LIKE %s OR role LIKE %s)
                          AND status = 'active'
                    ORDER BY name
                """, (search_pattern, search_pattern, search_pattern, 
                      search_pattern, search_pattern))
                has_department = False
            
            employees_data = cursor.fetchall()
            cursor.close()
            
            print(f"✅ DEBUG: Search found {len(employees_data)} employees")
            
            employees = []
            for data in employees_data:
                if has_department:
                    employee = cls(*data[:6], department=data[6], *data[7:])
                else:
                    employee = cls(*data)
                employees.append(employee)
            
            return employees
            
        except Exception as e:
            print(f"❌ DEBUG: Error searching employees: {e}")
            logging.error(f"Error searching employees: {e}")
            return []

    @classmethod
    def get_employee_by_id(cls, employee_code):
        """Get employee by employee code - LEGACY COMPATIBILITY"""
        try:
            print(f"🔍 DEBUG: Getting employee by code: {employee_code}")
            
            conn, cursor = get_db()
            
            # Try with department column first
            try:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, department, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE employee_code = %s AND status = 'active'
                """, (employee_code,))
                has_department = True
            except:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE employee_code = %s AND status = 'active'
                """, (employee_code,))
                has_department = False
            
            employee_data = cursor.fetchone()
            cursor.close()
            
            if employee_data:
                print(f"✅ DEBUG: Found employee: {employee_data[2]}")  # name
                if has_department:
                    return cls(*employee_data[:6], department=employee_data[6], *employee_data[7:])
                else:
                    return cls(*employee_data)
            
            print(f"❌ DEBUG: No employee found with code: {employee_code}")
            return None
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting employee by code: {e}")
            logging.error(f"Error getting employee by code: {e}")
            return None

    @classmethod
    def get_employee_by_code(cls, employee_code):
        """Get employee by code - More descriptive method name"""
        return cls.get_employee_by_id(employee_code)

    @classmethod
    def get_employee_by_database_id(cls, db_id):
        """Get employee by database ID"""
        try:
            conn, cursor = get_db()
            
            # Try with department column first
            try:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, department, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE id = %s AND status = 'active'
                """, (db_id,))
                has_department = True
            except:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE id = %s AND status = 'active'
                """, (db_id,))
                has_department = False
            
            employee_data = cursor.fetchone()
            cursor.close()
            
            if employee_data:
                if has_department:
                    return cls(*employee_data[:6], department=employee_data[6], *employee_data[7:])
                else:
                    return cls(*employee_data)
            return None
            
        except Exception as e:
            logging.error(f"Error getting employee by database ID: {e}")
            return None

    @classmethod
    def update_employee(cls, employee_code, **kwargs):
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Updating employee code: {employee_code}")
            print(f"🔍 DEBUG: Update kwargs: {kwargs}")
            
            conn, cursor = get_db()
            
            set_clauses = []
            values = []
            
            # Check if department column exists
            try:
                cursor.execute("DESCRIBE employees")
                columns = [row[0] for row in cursor.fetchall()]
                has_department_column = 'department' in columns
                print(f"🔍 DEBUG: Department column exists: {has_department_column}")
            except:
                has_department_column = False
            
            # Valid fields matching database schema
            valid_fields = [
                'employee_code', 'name', 'email', 'phone', 'role', 
                'password_hash', 'salary', 'hire_date', 'status'
            ]
            
            if has_department_column:
                valid_fields.append('department')
            
            for field, value in kwargs.items():
                if field == 'position' and value:
                    set_clauses.append("role = %s")
                    values.append(value.lower())
                    print(f"🔍 DEBUG: Converting position '{value}' to role in database")
                    continue
                if field == 'department':
                    if has_department_column:
                        set_clauses.append("department = %s")
                        values.append(value)
                        print(f"🔍 DEBUG: Updating department to '{value}'")
                    else:
                        print(f"🔍 DEBUG: Skipping department field '{value}' (column doesn't exist)")
                    continue
                
                if field == 'address':
                    print(f"🔍 DEBUG: Skipping address field (not stored in database)")
                    continue
                
                if field in valid_fields:
                    # Handle hire_date formatting
                    if field == 'hire_date' and value and isinstance(value, str):
                        if '-' in value and len(value.split('-')[0]) == 2:  # DD-MM-YYYY
                            try:
                                date_obj = datetime.strptime(value, '%d-%m-%Y')
                                value = date_obj.strftime('%Y-%m-%d')
                                print(f"🔍 DEBUG: Converted hire_date: {kwargs['hire_date']} -> {value}")
                            except ValueError:
                                print(f"🔍 DEBUG: Invalid hire_date format, keeping original: {value}")
                                pass
                    
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
                    print(f"🔍 DEBUG: Will update {field} = {value}")
            
            if not set_clauses:
                raise ValueError("No valid fields to update")
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(employee_code)
            
            query = f"UPDATE employees SET {', '.join(set_clauses)} WHERE employee_code = %s"
            
            print(f"🔍 DEBUG: Update query: {query}")
            print(f"🔍 DEBUG: Update values: {values}")
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                raise ValueError(f"No employee found with code {employee_code}")
            
            conn.commit()
            
            print(f"✅ DEBUG: Employee {employee_code} updated successfully")
            logging.info(f"Employee updated successfully: Code {employee_code}")
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error updating employee: {e}")
            logging.error(f"Error updating employee: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def delete_employee(cls, employee_code):
        """Soft delete employee - USING status FIELD"""
        try:
            conn, cursor = get_db()
            
            cursor.execute("SELECT name FROM employees WHERE employee_code = %s", (employee_code,))
            employee = cursor.fetchone()
            if not employee:
                cursor.close()
                raise ValueError(f"No employee found with code {employee_code}")
            
            cursor.execute("""
                UPDATE employees 
                SET status = 'inactive', updated_at = CURRENT_TIMESTAMP 
                WHERE employee_code = %s
            """, (employee_code,))
            
            conn.commit()
            cursor.close()
            
            print(f"✅ DEBUG: Employee {employee_code} deleted (status set to inactive)")
            logging.info(f"Employee deleted successfully: {employee[0]} (Code: {employee_code})")
            
        except Exception as e:
            print(f"❌ DEBUG: Error deleting employee: {e}")
            logging.error(f"Error deleting employee: {e}")
            if conn:
                conn.rollback()
            raise

    @classmethod
    def get_employees_by_role(cls, role):
        """Get employees by role"""
        try:
            print(f"🔍 DEBUG: Getting employees by role: {role}")
            
            conn, cursor = get_db()
            
            # Try with department column first
            try:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, department, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE role = %s AND status = 'active'
                    ORDER BY name
                """, (role,))
                has_department = True
            except:
                cursor.execute("""
                    SELECT id, employee_code, name, email, phone, role, password_hash, 
                           salary, hire_date, status, last_login, created_at, updated_at
                    FROM employees
                    WHERE role = %s AND status = 'active'
                    ORDER BY name
                """, (role,))
                has_department = False
            
            employees_data = cursor.fetchall()
            cursor.close()
            
            print(f"✅ DEBUG: Found {len(employees_data)} employees with role {role}")
            
            employees = []
            for data in employees_data:
                if has_department:
                    employee = cls(*data[:6], department=data[6], *data[7:])
                else:
                    employee = cls(*data)
                employees.append(employee)
            
            return employees
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting employees by role: {e}")
            logging.error(f"Error getting employees by role: {e}")
            return []

    @classmethod
    def get_employee_statistics(cls):
        """Get employee statistics - USING YOUR SCHEMA"""
        try:
            print("🔍 DEBUG: Getting employee statistics...")
            
            conn, cursor = get_db()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_employees,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_employees,
                    COUNT(CASE WHEN role = 'admin' THEN 1 END) as admin_count,
                    COUNT(CASE WHEN role = 'manager' THEN 1 END) as manager_count,
                    COUNT(CASE WHEN role = 'cashier' THEN 1 END) as cashier_count,
                    COUNT(CASE WHEN role = 'inventory_manager' THEN 1 END) as inventory_count,
                    AVG(CASE WHEN status = 'active' AND salary IS NOT NULL THEN salary END) as avg_salary
                FROM employees
            """)
            
            stats = cursor.fetchone()
            cursor.close()
            
            result = {
                'total_employees': stats[0] or 0,
                'active_employees': stats[1] or 0,
                'admin_count': stats[2] or 0,
                'manager_count': stats[3] or 0,
                'cashier_count': stats[4] or 0,
                'inventory_count': stats[5] or 0,
                'avg_salary': float(stats[6] or 0)
            }
            
            print(f"✅ DEBUG: Statistics calculated: {result}")
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting employee statistics: {e}")
            logging.error(f"Error getting employee statistics: {e}")
            return {
                'total_employees': 0,
                'active_employees': 0,
                'admin_count': 0,
                'manager_count': 0,
                'cashier_count': 0,
                'inventory_count': 0,
                'avg_salary': 0.0
            }

    def get_formatted_salary(self):
        """Get formatted salary"""
        if self.salary:
            return f"₹{self.salary:,.2f}"
        return "₹0.00"

    def get_formatted_hire_date(self):
        """Get formatted hire date"""
        if self.hire_date:
            if isinstance(self.hire_date, str):
                try:
                    date_obj = datetime.strptime(self.hire_date, '%Y-%m-%d').date()
                    return date_obj.strftime('%d-%m-%Y')
                except:
                    return self.hire_date
            else:
                return self.hire_date.strftime('%d-%m-%Y')
        return 'N/A'

    def get_years_of_service(self):
        """Calculate years of service"""
        if self.hire_date:
            try:
                if isinstance(self.hire_date, str):
                    hire_date = datetime.strptime(self.hire_date, '%Y-%m-%d').date()
                else:
                    hire_date = self.hire_date
                
                today = datetime.now().date()
                years = (today - hire_date).days / 365.25
                return round(years, 1)
            except:
                return 0
        return 0

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'employee_code': self.employee_code,
            'employee_id': self.employee_id,  # UI compatibility
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'position': self.position,  # UI compatibility
            'salary': float(self.salary) if self.salary else 0.0,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status,
            'is_active': self.is_active,  # UI compatibility
            'department': self.department,  # UI compatibility
            'address': self.address,  # UI compatibility
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'formatted_salary': self.get_formatted_salary(),
            'formatted_hire_date': self.get_formatted_hire_date(),
            'years_of_service': self.get_years_of_service()
        }

    def __str__(self):
        return f"Employee(id={self.id}, code='{self.employee_code}', name='{self.name}', role='{self.role}', dept='{self.department}')"

    def __repr__(self):
        return self.__str__()


# Testing utilities
def test_employee_operations():
    """Test employee operations"""
    try:
        print("🔍 Testing Employee model operations...")
        
        # Test database connection
        from database import get_db
        conn, cursor = get_db()
        cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'active'")
        db_count = cursor.fetchone()[0]
        cursor.close()
        print(f"✅ Database shows {db_count} active employees")
        
        # Test model
        employees = Employee.get_all_employees()
        print(f"✅ Employee model returned {len(employees)} employees")
        
        if employees:
            emp = employees[0]
            print(f"✅ First employee: {emp.name} (Code: {emp.employee_code})")
            print(f"   - Status: {emp.status}")
            print(f"   - Role: {emp.role}")
            print(f"   - Position: {emp.position}")
            print(f"   - Department: {emp.department}")
            print(f"   - Salary: {emp.get_formatted_salary()}")
        
        # Test compatibility method
        employees_compat = Employee.get_all()
        print(f"✅ Compatibility method returned {len(employees_compat)} employees")
        
        print("✅ All Employee model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Employee model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_employee_operations()
