"""
Database connection and management utilities
"""
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime
from config import DB_CONFIG, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
import hashlib
import os


class DatabaseManager:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self._connection = mysql.connector.connect(**DB_CONFIG)
            if self._connection.is_connected():
                logging.info("Database connection established successfully")
                self.create_tables()
            else:
                raise Error("Failed to establish database connection")
        except Error as e:
            logging.error(f"Database connection failed: {e}")
            raise
    
    def get_connection(self):
        """Get database connection with reconnection logic"""
        try:
            if not self._connection or not self._connection.is_connected():
                logging.info("Reconnecting to database...")
                self.connect()
            return self._connection
        except Error as e:
            logging.error(f"Error getting database connection: {e}")
            raise
    
    def get_cursor(self):
        """Get database cursor with dictionary support"""
        connection = self.get_connection()
        return connection.cursor(buffered=True, dictionary=False)
    
    def get_dict_cursor(self):
        """Get database cursor that returns dictionary results"""
        connection = self.get_connection()
        return connection.cursor(buffered=True, dictionary=True)
    
    def create_tables(self):

        cursor = self.get_cursor()
        
        try:
            # Disable foreign key checks temporarily
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            tables_to_create = [
                ("users", """
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        salt VARCHAR(255) NOT NULL,
                        role ENUM('admin', 'manager', 'cashier') NOT NULL,
                        email VARCHAR(255),
                        phone VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        
                        INDEX idx_username (username),
                        INDEX idx_role (role),
                        INDEX idx_active (is_active)
                    )
                """),
                
                ("suppliers", """
                    CREATE TABLE IF NOT EXISTS suppliers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        supplier_code VARCHAR(20) UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        contact_person VARCHAR(255),
                        phone VARCHAR(20),
                        email VARCHAR(255),
                        address TEXT,
                        city VARCHAR(100),
                        state VARCHAR(100),
                        pincode VARCHAR(10),
                        tax_id VARCHAR(50),
                        gst_number VARCHAR(20),
                        payment_terms VARCHAR(100),
                        credit_limit DECIMAL(15,4) DEFAULT 0.0000,
                        outstanding_amount DECIMAL(15,4) DEFAULT 0.0000,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        INDEX idx_supplier_code (supplier_code),
                        INDEX idx_active (is_active),
                        INDEX idx_gst_number (gst_number)
                    )
                """),
                
                ("employees", """
                    CREATE TABLE IF NOT EXISTS employees (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        employee_code VARCHAR(20) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        phone VARCHAR(20),
                        email VARCHAR(255) UNIQUE,
                        role ENUM('admin', 'manager', 'cashier', 'inventory_manager') DEFAULT 'cashier',
                        password_hash VARCHAR(255),
                        salary DECIMAL(12,2),
                        hire_date DATE,
                        status ENUM('active', 'inactive') DEFAULT 'active',
                        last_login TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        INDEX idx_employee_code (employee_code),
                        INDEX idx_email (email),
                        INDEX idx_role (role),
                        INDEX idx_status (status)
                    )
                """),
                
                ("customers", """
                    CREATE TABLE IF NOT EXISTS customers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_code VARCHAR(20) UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        phone VARCHAR(20) UNIQUE,
                        email VARCHAR(255),
                        address TEXT,
                        city VARCHAR(100),
                        state VARCHAR(100),
                        pincode VARCHAR(10),
                        date_of_birth DATE,
                        gender ENUM('male', 'female', 'other'),
                        membership_type ENUM('regular', 'silver', 'gold', 'platinum') DEFAULT 'regular',
                        loyalty_points INT DEFAULT 0,
                        total_purchases DECIMAL(15,4) DEFAULT 0.0000,
                        registration_date DATE DEFAULT (CURDATE()),
                        last_visit TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        INDEX idx_phone (phone),
                        INDEX idx_customer_code (customer_code),
                        INDEX idx_membership (membership_type),
                        INDEX idx_active (is_active),
                        FULLTEXT idx_customer_search (name, phone, email)
                    )
                """),
                
                ("categories", """
                    CREATE TABLE IF NOT EXISTS categories (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        description TEXT,
                        parent_category_id INT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (parent_category_id) REFERENCES categories(id) ON DELETE SET NULL,
                        INDEX idx_parent_category (parent_category_id),
                        INDEX idx_active (is_active)
                    )
                """),
                
                ("products", """
                    CREATE TABLE IF NOT EXISTS products (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        barcode VARCHAR(50) UNIQUE,
                        product_code VARCHAR(20) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        category_id INT,
                        supplier_id INT,
                        brand VARCHAR(100),
                        unit VARCHAR(50) DEFAULT 'piece',
                        unit_price DECIMAL(12,4) NOT NULL CHECK (unit_price >= 0),
                        cost_price DECIMAL(12,4) CHECK (cost_price >= 0),
                        mrp DECIMAL(12,4),
                        discount_percentage DECIMAL(5,2) DEFAULT 0.00,
                        tax_rate DECIMAL(5,2) DEFAULT 0.00,
                        quantity_in_stock INT NOT NULL DEFAULT 0,
                        min_stock_level INT DEFAULT 0,
                        max_stock_level INT DEFAULT 1000,
                        reorder_level INT DEFAULT 0,
                        expiry_date DATE,
                        manufacturing_date DATE,
                        batch_number VARCHAR(50),
                        rack_location VARCHAR(50),
                        weight_per_unit DECIMAL(8,3),
                        dimensions VARCHAR(100),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
                        FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
                        INDEX idx_barcode (barcode),
                        INDEX idx_product_code (product_code),
                        INDEX idx_category (category_id),
                        INDEX idx_supplier (supplier_id),
                        INDEX idx_active (is_active),
                        INDEX idx_stock_level (quantity_in_stock),
                        FULLTEXT idx_product_search (name, description, brand)
                    )
                """),
                
                ("transactions", """
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        transaction_number VARCHAR(50) UNIQUE NOT NULL,
                        customer_id INT,
                        employee_id INT NOT NULL,
                        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        transaction_type ENUM('sale', 'return', 'exchange') DEFAULT 'sale',
                        subtotal DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
                        discount_amount DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
                        tax_amount DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
                        total_amount DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
                        payment_method ENUM('cash', 'card', 'upi', 'credit', 'loyalty_points', 'mixed') DEFAULT 'cash',
                        payment_status ENUM('pending', 'completed', 'refunded', 'cancelled', 'partial') DEFAULT 'completed',
                        cash_received DECIMAL(15,4) DEFAULT 0.0000,
                        change_given DECIMAL(12,4) DEFAULT 0.0000,
                        loyalty_points_earned INT DEFAULT 0,
                        loyalty_points_redeemed INT DEFAULT 0,
                        notes TEXT,
                        shift_id INT,
                        pos_terminal VARCHAR(50),
                        receipt_printed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE RESTRICT,
                        INDEX idx_transaction_number (transaction_number),
                        INDEX idx_transaction_date (transaction_date),
                        INDEX idx_customer_id (customer_id),
                        INDEX idx_employee_id (employee_id),
                        INDEX idx_payment_method (payment_method),
                        INDEX idx_payment_status (payment_status),
                        INDEX idx_daily_sales (DATE(transaction_date), payment_status)
                    )
                """),
                
                ("transaction_items", """
                    CREATE TABLE IF NOT EXISTS transaction_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        transaction_id INT NOT NULL,
                        product_id INT NOT NULL,
                        quantity INT NOT NULL CHECK (quantity > 0),
                        unit_price DECIMAL(12,4) NOT NULL CHECK (unit_price >= 0),
                        original_price DECIMAL(12,4),
                        discount_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (discount_rate >= 0 AND discount_rate <= 100),
                        discount_amount DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
                        tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                        tax_amount DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
                        line_total DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
                        batch_number VARCHAR(50),
                        expiry_date DATE,
                        serial_numbers TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
                        INDEX idx_transaction_id (transaction_id),
                        INDEX idx_product_id (product_id),
                        INDEX idx_transaction_product (transaction_id, product_id)
                    )
                """),
                
                ("inventory_movements", """
                    CREATE TABLE IF NOT EXISTS inventory_movements (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        product_id INT NOT NULL,
                        movement_type ENUM('in', 'out', 'adjustment', 'transfer', 'damaged', 'expired') NOT NULL,
                        quantity INT NOT NULL,
                        reference_type ENUM('purchase', 'sale', 'return', 'adjustment', 'transfer', 'waste') NOT NULL,
                        reference_id INT,
                        reason VARCHAR(255),
                        employee_id INT NOT NULL,
                        movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        batch_number VARCHAR(50),
                        expiry_date DATE,
                        cost_per_unit DECIMAL(12,4),
                        notes TEXT,
                        
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE RESTRICT,
                        INDEX idx_product_movement (product_id, movement_date),
                        INDEX idx_movement_type (movement_type),
                        INDEX idx_movement_date (movement_date),
                        INDEX idx_reference (reference_type, reference_id)
                    )
                """),
                
                ("audit_logs", """
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        action VARCHAR(255) NOT NULL,
                        table_name VARCHAR(100),
                        record_id INT,
                        old_values JSON,
                        new_values JSON,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                        INDEX idx_user_id (user_id),
                        INDEX idx_table_record (table_name, record_id),
                        INDEX idx_created_at (created_at)
                    )
                """),
                
                ("system_settings", """
                    CREATE TABLE IF NOT EXISTS system_settings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        setting_key VARCHAR(100) UNIQUE NOT NULL,
                        setting_value TEXT,
                        data_type ENUM('string', 'integer', 'decimal', 'boolean', 'json') DEFAULT 'string',
                        description TEXT,
                        category VARCHAR(50),
                        is_editable BOOLEAN DEFAULT TRUE,
                        updated_by INT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
                        INDEX idx_category (category),
                        INDEX idx_key (setting_key)
                    )
                """)
            ]
            
            # Create each table with proper error handling
            successful_tables = 0
            for table_name, create_sql in tables_to_create:
                try:
                    cursor.execute(create_sql)
                    logging.info(f"Table '{table_name}' checked/created successfully")
                    successful_tables += 1
                except mysql.connector.Error as err:
                    if err.errno == 1050:  # Table already exists
                        logging.info(f"Table '{table_name}' already exists - skipping")
                        successful_tables += 1
                        continue
                    else:
                        logging.error(f"Error creating table '{table_name}': {err}")
                        continue
                except Exception as e:
                    logging.error(f"Unexpected error creating table '{table_name}': {e}")
                    continue
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            # Commit all changes
            self._connection.commit()
            logging.info(f"Database setup completed: {successful_tables}/{len(tables_to_create)} tables ready")
            
            # Insert default system settings
            self.insert_default_settings()
            
        except Exception as e:
            logging.error(f"Error in table creation process: {e}")
            self._connection.rollback()
        finally:
            if cursor:
                cursor.close()
        
        # Create default admin user
        self.create_default_admin()
    
    def insert_default_settings(self):
        """Insert default system settings"""
        cursor = None
        try:
            cursor = self.get_cursor()
            
            default_settings = [
                ('tax_rate', '18.00', 'decimal', 'Default GST rate percentage', 'finance'),
                ('discount_threshold', '1000.00', 'decimal', 'Minimum amount for automatic discount', 'finance'),
                ('discount_rate', '5.00', 'decimal', 'Automatic discount percentage', 'finance'),
                ('loyalty_points_ratio', '1', 'integer', 'Points earned per rupee spent', 'loyalty'),
                ('min_stock_alert', '10', 'integer', 'Minimum stock level for alerts', 'inventory'),
                ('receipt_footer', 'Thank you for shopping with us!', 'string', 'Receipt footer message', 'pos'),
                ('store_name', 'SuperMart Express', 'string', 'Store name for receipts', 'general'),
                ('store_address', '123 Main Street, City - 000001', 'string', 'Store address for receipts', 'general'),
                ('store_phone', '+91-9876543210', 'string', 'Store contact number', 'general'),
                ('currency_symbol', '₹', 'string', 'Currency symbol', 'general')
            ]
            
            for setting_key, setting_value, data_type, description, category in default_settings:
                cursor.execute("""
                    INSERT IGNORE INTO system_settings 
                    (setting_key, setting_value, data_type, description, category)
                    VALUES (%s, %s, %s, %s, %s)
                """, (setting_key, setting_value, data_type, description, category))
            
            self._connection.commit()
            logging.info("Default system settings inserted successfully")
            
        except Exception as e:
            logging.error(f"Error inserting default settings: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def create_default_admin(self):
        """Create default admin user if not exists"""
        cursor = None
        try:
            cursor = self.get_cursor()
            
            # Check if admin user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (DEFAULT_ADMIN_USERNAME,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                logging.info("Default admin user already exists - skipping creation")
                return
            
            # Create the default admin user
            salt = os.urandom(16).hex()
            hashed_password = hashlib.sha256((DEFAULT_ADMIN_PASSWORD + salt).encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, password, salt, role, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (DEFAULT_ADMIN_USERNAME, hashed_password, salt, 'admin', 'admin@supermart.com'))
            
            self._connection.commit()
            logging.info(f"Default admin user created successfully: {DEFAULT_ADMIN_USERNAME}")
            
        except mysql.connector.Error as db_err:
            logging.error(f"Database error creating default admin user: {db_err}")
        except Exception as e:
            logging.error(f"Unexpected error creating default admin user: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def verify_tables(self):
        """Verify that all required tables exist"""
        required_tables = [
            'users', 'employees', 'customers', 'suppliers', 'categories',
            'products', 'transactions', 'transaction_items', 
            'inventory_movements', 'audit_logs', 'system_settings'
        ]
        
        try:
            cursor = self.get_cursor()
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logging.warning(f"Missing tables: {missing_tables}")
                return False
            else:
                logging.info("All required tables exist")
                return True
                
        except Exception as e:
            logging.error(f"Error verifying tables: {e}")
            return False
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Execute a database query with proper error handling"""
        cursor = None
        try:
            cursor = self.get_cursor()
            cursor.execute(query, params or ())
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            
            if commit:
                self._connection.commit()
            
            return result
            
        except mysql.connector.Error as e:
            logging.error(f"Database query error: {e}")
            if commit:
                self._connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_table_info(self, table_name):
        """Get detailed information about a table"""
        try:
            cursor = self.get_cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'columns': columns,
                'row_count': row_count
            }
            
        except Exception as e:
            logging.error(f"Error getting table info for {table_name}: {e}")
            return None
    
    def close_connection(self):
        """Close database connection"""
        try:
            if self._connection and self._connection.is_connected():
                self._connection.close()
                logging.info("Database connection closed successfully")
        except Exception as e:
            logging.error(f"Error closing database connection: {e}")


def get_db():
    """Get database connection and cursor - Compatible with your existing code"""
    try:
        db_manager = DatabaseManager()
        connection = db_manager.get_connection()
        cursor = db_manager.get_cursor()
        return connection, cursor
    except Exception as e:
        logging.error(f"Error getting database connection: {e}")
        raise


def get_db_connection():
    """Alternative function name for compatibility"""
    return get_db()


def test_database_connection():
    """Test database connection and table creation"""
    try:
        db_manager = DatabaseManager()
        
        if db_manager.verify_tables():
            logging.info("✅ Database connection and tables verified successfully")
            
            # Test the decimal precision fix
            cursor = db_manager.get_cursor()
            cursor.execute("""
                SELECT 
                    CAST(123.4567 AS DECIMAL(15,4)) as test_decimal,
                    'Decimal precision test passed' as status
            """)
            result = cursor.fetchone()
            cursor.close()
            
            logging.info(f"✅ Decimal precision test: {result[0]} - {result[1]}")
            return True
        else:
            logging.error("❌ Some tables are missing")
            return False
            
    except Exception as e:
        logging.error(f"❌ Database test failed: {e}")
        return False


def get_system_setting(key, default_value=None):
    """Get a system setting value"""
    try:
        db_manager = DatabaseManager()
        cursor = db_manager.get_cursor()
        
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = %s", (key,))
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else default_value
        
    except Exception as e:
        logging.error(f"Error getting system setting {key}: {e}")
        return default_value


def set_system_setting(key, value, user_id=None):
    """Set a system setting value"""
    try:
        db_manager = DatabaseManager()
        cursor = db_manager.get_cursor()
        
        cursor.execute("""
            UPDATE system_settings 
            SET setting_value = %s, updated_by = %s, updated_at = NOW()
            WHERE setting_key = %s
        """, (value, user_id, key))
        
        db_manager._connection.commit()
        cursor.close()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        logging.error(f"Error setting system setting {key}: {e}")
        return False


# Utility functions for testing and debugging
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🔍 Testing database connection and setup...")
    
    if test_database_connection():
        print("✅ Database test passed!")
        
        # Additional tests
        try:
            db_manager = DatabaseManager()
            
            # Test table information
            tables = ['customers', 'employees', 'transactions', 'transaction_items']
            for table in tables:
                info = db_manager.get_table_info(table)
                if info:
                    print(f"📊 Table '{table}': {info['row_count']} rows, {len(info['columns'])} columns")
            
            # Test system settings
            tax_rate = get_system_setting('tax_rate', '18.00')
            print(f"💰 Current tax rate: {tax_rate}%")
            
        except Exception as e:
            print(f"❌ Additional tests failed: {e}")
    else:
        print("❌ Database test failed!")
