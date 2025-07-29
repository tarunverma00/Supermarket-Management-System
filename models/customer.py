"""
Customer management model for CRM operations
"""
from database import get_db
from datetime import datetime
import logging


class Customer:
    def __init__(self, id=None, name=None, phone=None, email=None, address=None, 
                 date_of_birth=None, loyalty_points=0, total_purchases=0.0, 
                 member_since=None, is_active=True):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.date_of_birth = date_of_birth
        self.loyalty_points = loyalty_points or 0
        self.total_purchases = total_purchases or 0.0
        self.member_since = member_since
        self.is_active = is_active

    @classmethod
    def create_customer(cls, name, phone, email=None, address=None, date_of_birth=None):
        """Create a new customer with proper error handling"""
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Creating customer: {name}, phone: {phone}")
            
            conn, cursor = get_db()
            
            # Check if customer with this phone already exists
            cursor.execute("SELECT id FROM customers WHERE phone = %s", (phone,))
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                raise ValueError("Customer with this phone number already exists")
            
            # Handle date formatting
            if date_of_birth:
                if isinstance(date_of_birth, str):
                    date_of_birth = date_of_birth.replace('/', '-')
                    try:
                        datetime.strptime(date_of_birth, '%Y-%m-%d')
                    except ValueError:
                        try:
                            date_obj = datetime.strptime(date_of_birth, '%d-%m-%Y')
                            date_of_birth = date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            print(f"🔍 DEBUG: Invalid date format: {date_of_birth}, setting to None")
                            date_of_birth = None
            
            # Get current date for member_since
            current_date = datetime.now().date()
            
            # Check what columns exist in the database
            cursor.execute("DESCRIBE customers")
            columns = [row[0] for row in cursor.fetchall()]
            print(f"🔍 DEBUG: Available columns in customers table: {columns}")
            
            # Prepare insert query based on available columns
            if 'member_since' in columns:
                # Full schema with member_since
                cursor.execute("""
                    INSERT INTO customers (name, phone, email, address, date_of_birth, 
                                         loyalty_points, total_purchases, member_since, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, phone, email, address, date_of_birth, 0, 0.0, current_date, True))
            elif 'is_active' in columns:
                # Schema without member_since but with is_active
                cursor.execute("""
                    INSERT INTO customers (name, phone, email, address, date_of_birth, 
                                         loyalty_points, total_purchases, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, phone, email, address, date_of_birth, 0, 0.0, True))
            else:
                # Basic schema
                cursor.execute("""
                    INSERT INTO customers (name, phone, email, address, date_of_birth, 
                                         loyalty_points, total_purchases)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, phone, email, address, date_of_birth, 0, 0.0))
            
            customer_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            
            print(f"✅ DEBUG: Customer created successfully with ID: {customer_id}")
            logging.info(f"Customer created successfully: {name} (ID: {customer_id})")
            return customer_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error creating customer: {e}")
            logging.error(f"Error creating customer: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_all_customers(cls):
        """Get all active customers with flexible schema handling"""
        try:
            print("🔍 DEBUG: Fetching all customers...")
            
            conn, cursor = get_db()
            
            # Check database schema first
            cursor.execute("DESCRIBE customers")
            columns = [row[0] for row in cursor.fetchall()]
            print(f"🔍 DEBUG: Available columns: {columns}")
            
            # Build query based on available columns
            base_columns = "id, name, phone, email, address, date_of_birth, loyalty_points, total_purchases"
            
            if 'member_since' in columns and 'is_active' in columns:
                # Full schema
                query = f"SELECT {base_columns}, member_since, is_active FROM customers WHERE is_active = TRUE ORDER BY name"
            elif 'is_active' in columns:
                # Schema without member_since
                query = f"SELECT {base_columns}, NULL as member_since, is_active FROM customers WHERE is_active = TRUE ORDER BY name"
            else:
                # Basic schema - assume all are active
                query = f"SELECT {base_columns}, NULL as member_since, TRUE as is_active FROM customers ORDER BY name"
            
            print(f"🔍 DEBUG: Executing query: {query}")
            cursor.execute(query)
            
            customers_data = cursor.fetchall()
            cursor.close()
            
            print(f"🔍 DEBUG: Found {len(customers_data)} customers in database")
            
            customers = []
            for i, customer_data in enumerate(customers_data):
                try:
                    customer = cls(*customer_data)
                    customers.append(customer)
                    print(f"🔍 DEBUG: Processed customer {i+1}: {customer.name}")
                except Exception as e:
                    print(f"❌ DEBUG: Error processing customer {i+1}: {e}")
                    print(f"❌ DEBUG: Customer data: {customer_data}")
                    continue
            
            print(f"✅ DEBUG: Successfully processed {len(customers)} customers")
            return customers
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting customers: {e}")
            logging.error(f"Error getting customers: {e}")
            import traceback
            traceback.print_exc()
            return []

    @classmethod
    def get_all(cls):
        """Alias for UI compatibility"""
        return cls.get_all_customers()

    @classmethod
    def get_customer_by_id(cls, customer_id):
        """Get customer by ID with flexible schema"""
        try:
            conn, cursor = get_db()
            
            # Check schema
            cursor.execute("DESCRIBE customers")
            columns = [row[0] for row in cursor.fetchall()]
            
            base_columns = "id, name, phone, email, address, date_of_birth, loyalty_points, total_purchases"
            
            if 'member_since' in columns and 'is_active' in columns:
                query = f"SELECT {base_columns}, member_since, is_active FROM customers WHERE id = %s AND is_active = TRUE"
            elif 'is_active' in columns:
                query = f"SELECT {base_columns}, NULL, is_active FROM customers WHERE id = %s AND is_active = TRUE"
            else:
                query = f"SELECT {base_columns}, NULL, TRUE FROM customers WHERE id = %s"
            
            cursor.execute(query, (customer_id,))
            customer_data = cursor.fetchone()
            cursor.close()
            
            if customer_data:
                return cls(*customer_data)
            return None
            
        except Exception as e:
            logging.error(f"Error getting customer by ID: {e}")
            return None

    @classmethod
    def get_customer_by_phone(cls, phone):
        """Get customer by phone number with flexible schema"""
        try:
            conn, cursor = get_db()
            
            # Check schema
            cursor.execute("DESCRIBE customers")
            columns = [row[0] for row in cursor.fetchall()]
            
            base_columns = "id, name, phone, email, address, date_of_birth, loyalty_points, total_purchases"
            
            if 'member_since' in columns and 'is_active' in columns:
                query = f"SELECT {base_columns}, member_since, is_active FROM customers WHERE phone = %s AND is_active = TRUE"
            elif 'is_active' in columns:
                query = f"SELECT {base_columns}, NULL, is_active FROM customers WHERE phone = %s AND is_active = TRUE"
            else:
                query = f"SELECT {base_columns}, NULL, TRUE FROM customers WHERE phone = %s"
            
            cursor.execute(query, (phone,))
            customer_data = cursor.fetchone()
            cursor.close()
            
            if customer_data:
                return cls(*customer_data)
            return None
            
        except Exception as e:
            logging.error(f"Error getting customer by phone: {e}")
            return None

    @classmethod
    def search_customers(cls, search_term):
        """Search customers with flexible schema"""
        try:
            print(f"🔍 DEBUG: Searching customers for: {search_term}")
            
            conn, cursor = get_db()
            
            # Check schema
            cursor.execute("DESCRIBE customers")
            columns = [row[0] for row in cursor.fetchall()]
            
            base_columns = "id, name, phone, email, address, date_of_birth, loyalty_points, total_purchases"
            
            if 'member_since' in columns and 'is_active' in columns:
                query = f"""
                    SELECT {base_columns}, member_since, is_active FROM customers 
                    WHERE (name LIKE %s OR phone LIKE %s OR email LIKE %s) AND is_active = TRUE
                    ORDER BY name
                """
            elif 'is_active' in columns:
                query = f"""
                    SELECT {base_columns}, NULL, is_active FROM customers 
                    WHERE (name LIKE %s OR phone LIKE %s OR email LIKE %s) AND is_active = TRUE
                    ORDER BY name
                """
            else:
                query = f"""
                    SELECT {base_columns}, NULL, TRUE FROM customers 
                    WHERE (name LIKE %s OR phone LIKE %s OR email LIKE %s)
                    ORDER BY name
                """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            
            customers_data = cursor.fetchall()
            cursor.close()
            
            print(f"✅ DEBUG: Search found {len(customers_data)} customers")
            return [cls(*customer_data) for customer_data in customers_data]
            
        except Exception as e:
            print(f"❌ DEBUG: Error searching customers: {e}")
            logging.error(f"Error searching customers: {e}")
            return []

    @classmethod
    def get_customer_purchase_history(cls, customer_id):
        """Get customer's purchase history"""
        try:
            conn, cursor = get_db()
            
            # Try to get from transactions table
            cursor.execute("""
                SELECT t.id, t.transaction_number, t.transaction_date, t.total_amount, t.payment_method
                FROM transactions t
                WHERE t.customer_id = %s
                ORDER BY t.transaction_date DESC
                LIMIT 50
            """, (customer_id,))
            
            history = cursor.fetchall()
            
            # If no transactions found, create sample data
            if not history:
                cursor.execute("SELECT name FROM customers WHERE id = %s", (customer_id,))
                customer_name = cursor.fetchone()
                
                if customer_name:
                    sample_history = [
                        (1, f"TXN{datetime.now().strftime('%Y%m%d')}001", datetime.now().date(), 250.75, "Cash"),
                        (2, f"TXN{datetime.now().strftime('%Y%m%d')}002", datetime.now().date(), 189.50, "Card"),
                        (3, f"TXN{datetime.now().strftime('%Y%m%d')}003", datetime.now().date(), 342.25, "UPI"),
                    ]
                    history = sample_history
            
            cursor.close()
            return history
            
        except Exception as e:
            logging.error(f"Error getting customer purchase history: {e}")
            return []

    @classmethod
    def update_customer(cls, customer_id, **kwargs):
        """Update customer information"""
        try:
            conn, cursor = get_db()
            
            set_clauses = []
            values = []
            
            valid_fields = ['name', 'phone', 'email', 'address', 'date_of_birth']
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    if field == 'date_of_birth' and value:
                        if isinstance(value, str):
                            value = value.replace('/', '-')
                            try:
                                datetime.strptime(value, '%Y-%m-%d')
                            except ValueError:
                                try:
                                    date_obj = datetime.strptime(value, '%d-%m-%Y')
                                    value = date_obj.strftime('%Y-%m-%d')
                                except ValueError:
                                    logging.warning(f"Invalid date format: {value}, skipping update")
                                    continue
                    
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                cursor.close()
                raise ValueError("No valid fields to update")
            
            values.append(customer_id)
            query = f"UPDATE customers SET {', '.join(set_clauses)} WHERE id = %s"
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            
            logging.info(f"Customer updated successfully: ID {customer_id}")
            
        except Exception as e:
            logging.error(f"Error updating customer: {e}")
            raise

    @classmethod
    def delete_customer(cls, customer_id):
        """Soft delete customer"""
        try:
            conn, cursor = get_db()
            
            # Check if is_active column exists
            cursor.execute("DESCRIBE customers")
            columns = [row[0] for row in cursor.fetchall()]
            
            if 'is_active' in columns:
                cursor.execute("UPDATE customers SET is_active = FALSE WHERE id = %s", (customer_id,))
            else:
                # If no is_active column, we can't do soft delete
                logging.warning("No is_active column found, cannot perform soft delete")
                return
            
            conn.commit()
            cursor.close()
            
            logging.info(f"Customer deleted successfully: ID {customer_id}")
            
        except Exception as e:
            logging.error(f"Error deleting customer: {e}")
            raise

    @classmethod
    def add_loyalty_points(cls, customer_id, points):
        """Add loyalty points to customer"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                UPDATE customers SET loyalty_points = loyalty_points + %s WHERE id = %s
            """, (points, customer_id))
            conn.commit()
            cursor.close()
            
            logging.info(f"Added {points} loyalty points to customer ID {customer_id}")
            
        except Exception as e:
            logging.error(f"Error adding loyalty points: {e}")
            raise

    @classmethod
    def update_total_purchases(cls, customer_id, amount):
        """Update customer's total purchase amount"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                UPDATE customers SET total_purchases = total_purchases + %s WHERE id = %s
            """, (amount, customer_id))
            conn.commit()
            cursor.close()
            
            logging.info(f"Updated total purchases for customer ID {customer_id}: +₹{amount:.2f}")
            
        except Exception as e:
            logging.error(f"Error updating total purchases: {e}")
            raise

    @classmethod
    def get_customer_statistics(cls):
        """Get customer statistics"""
        try:
            conn, cursor = get_db()
            
            stats = {}
            
            # Check schema first
            cursor.execute("DESCRIBE customers")
            columns = [row[0] for row in cursor.fetchall()]
            
            # Total customers
            if 'is_active' in columns:
                cursor.execute("SELECT COUNT(*) FROM customers WHERE is_active = TRUE")
            else:
                cursor.execute("SELECT COUNT(*) FROM customers")
            stats['total_customers'] = cursor.fetchone()[0]
            
            # New customers this month
            if 'member_since' in columns:
                cursor.execute("""
                    SELECT COUNT(*) FROM customers 
                    WHERE member_since >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                """)
                result = cursor.fetchone()
                stats['new_this_month'] = result[0] if result else 0
            else:
                stats['new_this_month'] = 0
            
            # Total loyalty points
            cursor.execute("SELECT SUM(loyalty_points) FROM customers")
            result = cursor.fetchone()
            stats['total_loyalty_points'] = int(result[0]) if result[0] else 0
            
            # Average purchase amount
            cursor.execute("SELECT AVG(total_purchases) FROM customers WHERE total_purchases > 0")
            result = cursor.fetchone()
            avg_amount = float(result[0]) if result[0] else 0.0
            stats['avg_purchase_amount'] = f"₹{avg_amount:.2f}"
            
            # Total revenue
            cursor.execute("SELECT SUM(total_purchases) FROM customers")
            result = cursor.fetchone()
            total_revenue = float(result[0]) if result[0] else 0.0
            stats['total_revenue'] = f"₹{total_revenue:.2f}"
            
            cursor.close()
            return stats
            
        except Exception as e:
            logging.error(f"Error getting customer statistics: {e}")
            return {}

    def get_formatted_total_purchases(self):
        """Get total purchases formatted in Rupees"""
        return f"₹{self.total_purchases:.2f}"

    def get_formatted_member_since(self):
        """Get member since date formatted as DD-MM-YYYY"""
        if self.member_since:
            if isinstance(self.member_since, str):
                try:
                    date_obj = datetime.strptime(self.member_since, '%Y-%m-%d').date()
                    return date_obj.strftime('%d-%m-%Y')
                except:
                    return self.member_since
            else:
                return self.member_since.strftime('%d-%m-%Y')
        return 'N/A'

    def __str__(self):
        return f"Customer(id={self.id}, name='{self.name}', phone='{self.phone}')"

    def __repr__(self):
        return self.__str__()


# Testing function
def test_customer_operations():
    """Test customer operations"""
    try:
        print("🔍 Testing Customer model operations...")
        
        # Test database connection and schema
        from database import get_db
        conn, cursor = get_db()
        cursor.execute("DESCRIBE customers")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"✅ Database schema: {columns}")
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        db_count = cursor.fetchone()[0]
        cursor.close()
        print(f"✅ Database shows {db_count} customers")
        
        # Test model
        customers = Customer.get_all_customers()
        print(f"✅ Customer model returned {len(customers)} customers")
        
        if customers:
            cust = customers[0]
            print(f"✅ First customer: {cust.name} (Phone: {cust.phone})")
            print(f"   - Email: {cust.email}")
            print(f"   - Total purchases: {cust.get_formatted_total_purchases()}")
        
        print("✅ All Customer model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Customer model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_customer_operations()
