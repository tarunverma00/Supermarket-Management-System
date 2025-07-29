"""
Product and inventory management model
"""
from database import get_db
from datetime import datetime, timedelta
import logging

class Product:
    def __init__(self, id=None, product_code=None, barcode=None, name=None, description=None, 
                 category=None, category_id=None, supplier_id=None, brand=None, unit=None,
                 unit_price=None, cost_price=None, mrp=None, discount_percentage=None,
                 tax_rate=None, quantity_in_stock=0, min_stock_level=0, max_stock_level=1000,
                 reorder_level=0, expiry_date=None, manufacturing_date=None, batch_number=None,
                 rack_location=None, weight_per_unit=None, dimensions=None, is_active=True,
                 created_at=None, updated_at=None):
        
        self.id = id
        self.product_code = product_code
        self.barcode = barcode
        self.name = name
        self.description = description
        self.category = category
        self.category_id = category_id
        self.supplier_id = supplier_id
        self.brand = brand
        self.unit = unit or 'piece'
        self.unit_price = unit_price
        self.cost_price = cost_price
        self.mrp = mrp
        self.discount_percentage = discount_percentage or 0.0
        self.tax_rate = tax_rate or 18.0
        self.quantity_in_stock = quantity_in_stock
        self.min_stock_level = min_stock_level
        self.max_stock_level = max_stock_level
        self.reorder_level = reorder_level
        self.expiry_date = expiry_date
        self.manufacturing_date = manufacturing_date
        self.batch_number = batch_number
        self.rack_location = rack_location
        self.weight_per_unit = weight_per_unit
        self.dimensions = dimensions
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        
        #  compatibility properties for billing system
        self.discount_rate = self.discount_percentage  # Billing expects discount_rate
        self.price = self.unit_price  # Billing might expect price instead of unit_price
        self.stock_quantity = self.quantity_in_stock  # Alternative stock field name
        self.supplier = supplier_id  # Simple supplier reference

    # Add compatibility properties as methods for billing system
    @property 
    def selling_price(self):
        """Get the current selling price (unit_price)"""
        return self.unit_price or 0.0
    
    @property
    def current_stock(self):
        """Get current stock quantity"""
        return self.quantity_in_stock or 0
    
    def get_discounted_price(self):
        """Calculate price after discount"""
        if self.unit_price and self.discount_percentage:
            discount_amount = self.unit_price * (self.discount_percentage / 100)
            return self.unit_price - discount_amount
        return self.unit_price or 0.0
    
    def get_discount_amount(self):
        """Get the discount amount in currency"""
        if self.unit_price and self.discount_percentage:
            return self.unit_price * (self.discount_percentage / 100)
        return 0.0
    
    def get_tax_amount(self):
        """Calculate tax amount"""
        price = self.get_discounted_price()
        if price and self.tax_rate:
            return price * (self.tax_rate / 100)
        return 0.0
    
    def get_final_price(self):
        """Get final price including discount and tax"""
        discounted_price = self.get_discounted_price()
        tax_amount = self.get_tax_amount()
        return discounted_price + tax_amount

    @staticmethod
    def generate_product_code():
        """Generate unique product code"""
        try:
            conn, cursor = get_db()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            cursor.close()
            return f"PRD{count + 1:05d}"  # PRD00001, PRD00002, etc.
        except Exception as e:
            logging.error(f"Error generating product code: {e}")
            return f"PRD{datetime.now().strftime('%Y%m%d%H%M%S')}"

    @classmethod
    def create_product(cls, name, unit_price, quantity_in_stock=0, **kwargs):
       
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Creating product: {name}")
            
            conn, cursor = get_db()
            
            # Generate product_code if not provided
            product_code = kwargs.get('product_code')
            if not product_code:
                product_code = cls.generate_product_code()
                print(f"🔍 DEBUG: Generated product_code: {product_code}")
            
            # Handle barcode
            barcode = kwargs.get('barcode')
            if barcode:
                # Check if barcode already exists
                cursor.execute("SELECT id FROM products WHERE barcode = %s", (barcode,))
                if cursor.fetchone():
                    raise ValueError("Product with this barcode already exists")
            
            # Handle date formatting
            expiry_date = kwargs.get('expiry_date')
            if expiry_date and isinstance(expiry_date, str):
                if '/' in expiry_date:
                    expiry_date = expiry_date.replace('/', '-')
            
            manufacturing_date = kwargs.get('manufacturing_date')
            if manufacturing_date and isinstance(manufacturing_date, str):
                if '/' in manufacturing_date:
                    manufacturing_date = manufacturing_date.replace('/', '-')
            
            product_data = {
                'product_code': product_code,
                'barcode': barcode,
                'name': name,
                'description': kwargs.get('description'),
                'category_id': kwargs.get('category_id'),  # ONLY category_id, removed 'category'
                'supplier_id': kwargs.get('supplier_id'),
                'brand': kwargs.get('brand'),
                'unit': kwargs.get('unit', 'piece'),
                'unit_price': float(unit_price),
                'cost_price': kwargs.get('cost_price'),
                'mrp': kwargs.get('mrp'),
                'discount_percentage': kwargs.get('discount_percentage', 0.0),
                'tax_rate': kwargs.get('tax_rate', 18.0),
                'quantity_in_stock': int(quantity_in_stock),
                'min_stock_level': kwargs.get('min_stock_level', 0),
                'max_stock_level': kwargs.get('max_stock_level', 1000),
                'reorder_level': kwargs.get('reorder_level', 0),
                'expiry_date': expiry_date,
                'manufacturing_date': manufacturing_date,
                'batch_number': kwargs.get('batch_number'),
                'rack_location': kwargs.get('rack_location'),
                'weight_per_unit': kwargs.get('weight_per_unit'),
                'dimensions': kwargs.get('dimensions'),
                'is_active': kwargs.get('is_active', True)
            }
            
            print(f"🔍 DEBUG: Product data prepared: {product_data}")
            
            cursor.execute("""
                INSERT INTO products (
                    product_code, barcode, name, description, category_id, 
                    supplier_id, brand, unit, unit_price, cost_price, mrp, 
                    discount_percentage, tax_rate, quantity_in_stock, min_stock_level, 
                    max_stock_level, reorder_level, expiry_date, manufacturing_date, 
                    batch_number, rack_location, weight_per_unit, dimensions, is_active
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                product_data['product_code'], product_data['barcode'], product_data['name'],
                product_data['description'], product_data['category_id'],  # REMOVED category
                product_data['supplier_id'], product_data['brand'], product_data['unit'],
                product_data['unit_price'], product_data['cost_price'], product_data['mrp'],
                product_data['discount_percentage'], product_data['tax_rate'], product_data['quantity_in_stock'],
                product_data['min_stock_level'], product_data['max_stock_level'], product_data['reorder_level'],
                product_data['expiry_date'], product_data['manufacturing_date'], product_data['batch_number'],
                product_data['rack_location'], product_data['weight_per_unit'], product_data['dimensions'],
                product_data['is_active']
            ))
            
            product_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ DEBUG: Product created with ID: {product_id}")
            
            # Log inventory movement for initial stock
            if quantity_in_stock > 0:
                cls.log_inventory_movement(
                    product_id, 'in', quantity_in_stock, 'Initial stock', 
                    kwargs.get('employee_id')
                )
            
            logging.info(f"Product created successfully: {name} (Code: {product_code})")
            return product_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error creating product: {e}")
            logging.error(f"Error creating product: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def add_product(cls, product_data):
        """Add product with data dictionary - Compatibility method"""
        try:
            return cls.create_product(
                name=product_data['name'],
                unit_price=product_data['unit_price'],
                quantity_in_stock=product_data.get('quantity_in_stock', 0),
                **product_data
            )
        except Exception as e:
            logging.error(f"Error adding product: {e}")
            raise

    @classmethod
    def get_all_products(cls):
        try:
            conn, cursor = get_db()
            cursor.execute("""
                SELECT id, product_code, barcode, name, description, category_id,
                       supplier_id, brand, unit, unit_price, cost_price, mrp, 
                       discount_percentage, tax_rate, quantity_in_stock, min_stock_level,
                       max_stock_level, reorder_level, expiry_date, manufacturing_date,
                       batch_number, rack_location, weight_per_unit, dimensions, is_active,
                       created_at, updated_at
                FROM products
                WHERE is_active = TRUE
                ORDER BY name
            """)
            
            products_data = cursor.fetchall()
            cursor.close()
            
            products = []
            for data in products_data:
                product = cls(
                    id=data[0], product_code=data[1], barcode=data[2], name=data[3], 
                    description=data[4], category_id=data[5], supplier_id=data[6],
                    brand=data[7], unit=data[8], unit_price=data[9], cost_price=data[10],
                    mrp=data[11], discount_percentage=data[12], tax_rate=data[13],
                    quantity_in_stock=data[14], min_stock_level=data[15], max_stock_level=data[16],
                    reorder_level=data[17], expiry_date=data[18], manufacturing_date=data[19],
                    batch_number=data[20], rack_location=data[21], weight_per_unit=data[22],
                    dimensions=data[23], is_active=data[24], created_at=data[25], updated_at=data[26]
                )
                products.append(product)
            
            print(f"✅ DEBUG: Retrieved {len(products)} products")
            return products
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting products: {e}")
            logging.error(f"Error getting products: {e}")
            return []

    @classmethod
    def get_all(cls):
        """Alias for compatibility with billing system"""
        return cls.get_all_products()

    @classmethod
    def search_products(cls, search_term):
        """Search products by name, barcode, brand, or product_code"""
        try:
            conn, cursor = get_db()
            search_pattern = f"%{search_term}%"
            
            cursor.execute("""
                SELECT id, product_code, barcode, name, description, category_id,
                       supplier_id, brand, unit, unit_price, cost_price, mrp, 
                       discount_percentage, tax_rate, quantity_in_stock, min_stock_level,
                       max_stock_level, reorder_level, expiry_date, manufacturing_date,
                       batch_number, rack_location, weight_per_unit, dimensions, is_active,
                       created_at, updated_at
                FROM products
                WHERE (name LIKE %s OR barcode LIKE %s OR brand LIKE %s OR product_code LIKE %s) 
                      AND is_active = TRUE
                ORDER BY name
            """, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            products_data = cursor.fetchall()
            cursor.close()
            
            products = []
            for data in products_data:
                product = cls(
                    id=data[0], product_code=data[1], barcode=data[2], name=data[3], 
                    description=data[4], category_id=data[5], supplier_id=data[6],
                    brand=data[7], unit=data[8], unit_price=data[9], cost_price=data[10],
                    mrp=data[11], discount_percentage=data[12], tax_rate=data[13],
                    quantity_in_stock=data[14], min_stock_level=data[15], max_stock_level=data[16],
                    reorder_level=data[17], expiry_date=data[18], manufacturing_date=data[19],
                    batch_number=data[20], rack_location=data[21], weight_per_unit=data[22],
                    dimensions=data[23], is_active=data[24], created_at=data[25], updated_at=data[26]
                )
                products.append(product)
            
            print(f"✅ DEBUG: Search found {len(products)} products for '{search_term}'")
            return products
            
        except Exception as e:
            print(f"❌ DEBUG: Error searching products: {e}")
            logging.error(f"Error searching products: {e}")
            return []

    @classmethod
    def get_product_by_barcode(cls, barcode):
        """Get product by barcode - ENHANCED"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                SELECT id, product_code, barcode, name, description, category_id,
                       supplier_id, brand, unit, unit_price, cost_price, mrp, 
                       discount_percentage, tax_rate, quantity_in_stock, min_stock_level,
                       max_stock_level, reorder_level, expiry_date, manufacturing_date,
                       batch_number, rack_location, weight_per_unit, dimensions, is_active,
                       created_at, updated_at
                FROM products 
                WHERE barcode = %s AND is_active = TRUE
            """, (barcode,))
            
            product_data = cursor.fetchone()
            cursor.close()
            
            if product_data:
                print(f"✅ DEBUG: Found product by barcode: {barcode}")
                return cls(
                    id=product_data[0], product_code=product_data[1], barcode=product_data[2], 
                    name=product_data[3], description=product_data[4], category_id=product_data[5], 
                    supplier_id=product_data[6], brand=product_data[7], unit=product_data[8], 
                    unit_price=product_data[9], cost_price=product_data[10], mrp=product_data[11], 
                    discount_percentage=product_data[12], tax_rate=product_data[13], 
                    quantity_in_stock=product_data[14], min_stock_level=product_data[15], 
                    max_stock_level=product_data[16], reorder_level=product_data[17], 
                    expiry_date=product_data[18], manufacturing_date=product_data[19], 
                    batch_number=product_data[20], rack_location=product_data[21], 
                    weight_per_unit=product_data[22], dimensions=product_data[23], 
                    is_active=product_data[24], created_at=product_data[25], updated_at=product_data[26]
                )
            
            print(f"❌ DEBUG: No product found with barcode: {barcode}")
            return None
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting product by barcode: {e}")
            logging.error(f"Error getting product by barcode: {e}")
            return None

    @classmethod
    def get_product_by_id(cls, product_id):
        """Get product by ID - ENHANCED"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                SELECT id, product_code, barcode, name, description, category_id,
                       supplier_id, brand, unit, unit_price, cost_price, mrp, 
                       discount_percentage, tax_rate, quantity_in_stock, min_stock_level,
                       max_stock_level, reorder_level, expiry_date, manufacturing_date,
                       batch_number, rack_location, weight_per_unit, dimensions, is_active,
                       created_at, updated_at
                FROM products 
                WHERE id = %s AND is_active = TRUE
            """, (product_id,))
            
            product_data = cursor.fetchone()
            cursor.close()
            
            if product_data:
                return cls(
                    id=product_data[0], product_code=product_data[1], barcode=product_data[2], 
                    name=product_data[3], description=product_data[4], category_id=product_data[5], 
                    supplier_id=product_data[6], brand=product_data[7], unit=product_data[8], 
                    unit_price=product_data[9], cost_price=product_data[10], mrp=product_data[11], 
                    discount_percentage=product_data[12], tax_rate=product_data[13], 
                    quantity_in_stock=product_data[14], min_stock_level=product_data[15], 
                    max_stock_level=product_data[16], reorder_level=product_data[17], 
                    expiry_date=product_data[18], manufacturing_date=product_data[19], 
                    batch_number=product_data[20], rack_location=product_data[21], 
                    weight_per_unit=product_data[22], dimensions=product_data[23], 
                    is_active=product_data[24], created_at=product_data[25], updated_at=product_data[26]
                )
            return None
            
        except Exception as e:
            logging.error(f"Error getting product by ID: {e}")
            return None

    @classmethod
    def update_product(cls, product_id, **kwargs):
        """Update product information - ENHANCED"""
        conn = None
        cursor = None
        
        try:
            conn, cursor = get_db()
            
            set_clauses = []
            values = []
            valid_fields = [
                'product_code', 'barcode', 'name', 'description', 'category_id',
                'supplier_id', 'brand', 'unit', 'unit_price', 'cost_price', 'mrp',
                'discount_percentage', 'tax_rate', 'quantity_in_stock', 'min_stock_level',
                'max_stock_level', 'reorder_level', 'expiry_date', 'manufacturing_date',
                'batch_number', 'rack_location', 'weight_per_unit', 'dimensions', 'is_active'
            ]
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    # Handle date format conversion
                    if field in ['expiry_date', 'manufacturing_date'] and value and isinstance(value, str):
                        if '/' in value:
                            value = value.replace('/', '-')
                    
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                raise ValueError("No valid fields to update")
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(product_id)
            
            query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = %s"
            
            cursor.execute(query, values)
            conn.commit()
            
            print(f"✅ DEBUG: Product {product_id} updated successfully")
            logging.info(f"Product updated successfully: ID {product_id}")
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error updating product: {e}")
            logging.error(f"Error updating product: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def update_product_by_barcode(cls, barcode, **kwargs):
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Updating product by barcode: {barcode}")
            print(f"🔍 DEBUG: Update data: {kwargs}")
            
            conn, cursor = get_db()
            
            # First, get the product ID by barcode
            cursor.execute("SELECT id FROM products WHERE barcode = %s AND is_active = TRUE", (barcode,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"No product found with barcode: {barcode}")
            
            product_id = result[0]
            print(f"🔍 DEBUG: Found product ID: {product_id} for barcode: {barcode}")
            
            set_clauses = []
            values = []
            valid_fields = [
                'product_code', 'barcode', 'name', 'description', 'category_id',
                'supplier_id', 'brand', 'unit', 'unit_price', 'cost_price', 'mrp',
                'discount_percentage', 'tax_rate', 'quantity_in_stock', 'min_stock_level',
                'max_stock_level', 'reorder_level', 'expiry_date', 'manufacturing_date',
                'batch_number', 'rack_location', 'weight_per_unit', 'dimensions', 'is_active'
            ]
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    # Handle date format conversion
                    if field in ['expiry_date', 'manufacturing_date'] and value and isinstance(value, str):
                        if '/' in value:
                            value = value.replace('/', '-')
                    
                    # Handle numeric fields
                    if field in ['unit_price', 'cost_price', 'mrp', 'discount_percentage', 'tax_rate']:
                        try:
                            value = float(value) if value else 0.0
                        except (ValueError, TypeError):
                            print(f"🔍 DEBUG: Invalid numeric value for {field}: {value}, skipping")
                            continue
                    
                    if field in ['quantity_in_stock', 'min_stock_level', 'max_stock_level', 'reorder_level']:
                        try:
                            value = int(value) if value else 0
                        except (ValueError, TypeError):
                            print(f"🔍 DEBUG: Invalid integer value for {field}: {value}, skipping")
                            continue
                    
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
                    print(f"🔍 DEBUG: Will update {field} = {value}")
            
            if not set_clauses:
                raise ValueError("No valid fields to update")
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(barcode)
            
            query = f"UPDATE products SET {', '.join(set_clauses)} WHERE barcode = %s AND is_active = TRUE"
            
            print(f"🔍 DEBUG: Update query: {query}")
            print(f"🔍 DEBUG: Update values: {values}")
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                raise ValueError(f"No product updated with barcode: {barcode}")
            
            conn.commit()
            
            print(f"✅ DEBUG: Product with barcode {barcode} updated successfully")
            logging.info(f"Product updated successfully by barcode: {barcode}")
            
            # Log inventory movement if quantity changed
            if 'quantity_in_stock' in kwargs:
                cls.log_inventory_movement(
                    product_id, 'adjustment', abs(int(kwargs['quantity_in_stock'])), 
                    'Stock update via barcode', kwargs.get('employee_id')
                )
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error updating product by barcode: {e}")
            logging.error(f"Error updating product by barcode: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def delete_product(cls, product_id):
        """Soft delete product (set is_active to False)"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                UPDATE products 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, (product_id,))
            
            if cursor.rowcount == 0:
                cursor.close()
                raise ValueError("Product not found")
            
            conn.commit()
            cursor.close()
            
            print(f"✅ DEBUG: Product {product_id} deleted (soft delete)")
            logging.info(f"Product deleted successfully: ID {product_id}")
            
        except Exception as e:
            print(f"❌ DEBUG: Error deleting product: {e}")
            logging.error(f"Error deleting product: {e}")
            raise

    @classmethod
    def delete_product_by_barcode(cls, barcode):
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Deleting product by barcode: {barcode}")
            
            conn, cursor = get_db()
            
            # First, get the product ID and name by barcode
            cursor.execute("SELECT id, name FROM products WHERE barcode = %s AND is_active = TRUE", (barcode,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"No product found with barcode: {barcode}")
            
            product_id, product_name = result
            print(f"🔍 DEBUG: Found product ID: {product_id}, Name: {product_name} for barcode: {barcode}")
            
            # Soft delete the product (set is_active to False)
            cursor.execute("""
                UPDATE products 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP 
                WHERE barcode = %s AND is_active = TRUE
            """, (barcode,))
            
            if cursor.rowcount == 0:
                raise ValueError(f"No product deleted with barcode: {barcode}")
            
            conn.commit()
            
            print(f"✅ DEBUG: Product with barcode {barcode} deleted successfully")
            logging.info(f"Product deleted successfully by barcode: {barcode} (Name: {product_name})")
            
            # Log inventory movement for deletion
            cls.log_inventory_movement(
                product_id, 'out', 0, f'Product deleted via barcode: {barcode}', 
                None  # employee_id can be added if available
            )
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error deleting product by barcode: {e}")
            logging.error(f"Error deleting product by barcode: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def update_stock(cls, product_id, quantity_change, reason="Manual adjustment", employee_id=None):
        """Update product stock and log movement - ENHANCED"""
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Updating stock for product {product_id}, change: {quantity_change}")
            
            conn, cursor = get_db()
            
            # Get current stock
            cursor.execute("SELECT quantity_in_stock, name FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Product not found")
                
            current_stock, product_name = result
            new_stock = current_stock + quantity_change
            
            if new_stock < 0:
                raise ValueError(f"Insufficient stock available. Current: {current_stock}, Requested: {abs(quantity_change)}")
            
            # Update stock
            cursor.execute("""
                UPDATE products SET quantity_in_stock = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, (new_stock, product_id))
            
            conn.commit()
            
            print(f"✅ DEBUG: Stock updated - {product_name}: {current_stock} → {new_stock}")
            
            # Log inventory movement
            movement_type = 'in' if quantity_change > 0 else 'out'
            cls.log_inventory_movement(product_id, movement_type, abs(quantity_change), reason, employee_id)
            
            logging.info(f"Stock updated for product ID {product_id}: {quantity_change} units")
            return new_stock
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Error updating stock: {e}")
            logging.error(f"Error updating stock: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def log_inventory_movement(cls, product_id, movement_type, quantity, reason, employee_id=None):
        """Log inventory movements for audit trail - ENHANCED"""
        try:
            conn, cursor = get_db()
            
            # Determine reference_type based on reason
            reference_type = 'adjustment'  # default
            if 'sale' in reason.lower() or 'transaction' in reason.lower():
                reference_type = 'sale'
            elif 'purchase' in reason.lower() or 'initial' in reason.lower():
                reference_type = 'purchase'
            elif 'return' in reason.lower():
                reference_type = 'return'
            
            cursor.execute("""
                INSERT INTO inventory_movements 
                (product_id, movement_type, quantity, reference_type, reason, employee_id, movement_date)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (product_id, movement_type, quantity, reference_type, reason, employee_id))
            
            conn.commit()
            cursor.close()
            
            print(f"✅ DEBUG: Inventory movement logged: {movement_type} {quantity} units - {reason}")
            
        except Exception as e:
            print(f"❌ DEBUG: Error logging inventory movement: {e}")
            logging.error(f"Error logging inventory movement: {e}")

    @classmethod
    def get_low_stock_products(cls):
        """Get products with stock below reorder level"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                SELECT id, product_code, barcode, name, quantity_in_stock, min_stock_level, reorder_level
                FROM products 
                WHERE quantity_in_stock <= GREATEST(min_stock_level, reorder_level) 
                      AND is_active = TRUE
                ORDER BY quantity_in_stock ASC
            """)
            
            low_stock_data = cursor.fetchall()
            cursor.close()
            
            print(f"✅ DEBUG: Found {len(low_stock_data)} low stock products")
            return low_stock_data
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting low stock products: {e}")
            logging.error(f"Error getting low stock products: {e}")
            return []

    @classmethod
    def get_expiring_products(cls, days=7):
        """Get products expiring within specified days"""
        try:
            conn, cursor = get_db()
            expiry_threshold = datetime.now().date() + timedelta(days=days)
            
            cursor.execute("""
                SELECT id, product_code, barcode, name, expiry_date, quantity_in_stock
                FROM products 
                WHERE expiry_date IS NOT NULL 
                      AND expiry_date <= %s 
                      AND expiry_date >= CURDATE() 
                      AND is_active = TRUE
                ORDER BY expiry_date ASC
            """, (expiry_threshold,))
            
            expiring_data = cursor.fetchall()
            cursor.close()
            
            print(f"✅ DEBUG: Found {len(expiring_data)} expiring products")
            return expiring_data
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting expiring products: {e}")
            logging.error(f"Error getting expiring products: {e}")
            return []

    @classmethod
    def get_inventory_movements(cls, product_id=None, days=30):
        """Get inventory movements for a product or all products"""
        try:
            conn, cursor = get_db()
            
            if product_id:
                cursor.execute("""
                    SELECT im.id, im.product_id, p.name as product_name, p.product_code,
                           im.movement_type, im.quantity, im.reference_type, im.reason,
                           im.movement_date, e.name as employee_name
                    FROM inventory_movements im
                    LEFT JOIN products p ON im.product_id = p.id
                    LEFT JOIN employees e ON im.employee_id = e.id
                    WHERE im.product_id = %s
                          AND im.movement_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY im.movement_date DESC
                """, (product_id, days))
            else:
                cursor.execute("""
                    SELECT im.id, im.product_id, p.name as product_name, p.product_code,
                           im.movement_type, im.quantity, im.reference_type, im.reason,
                           im.movement_date, e.name as employee_name
                    FROM inventory_movements im
                    LEFT JOIN products p ON im.product_id = p.id
                    LEFT JOIN employees e ON im.employee_id = e.id
                    WHERE im.movement_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY im.movement_date DESC
                    LIMIT 100
                """, (days,))
            
            movements = cursor.fetchall()
            cursor.close()
            
            return movements
            
        except Exception as e:
            logging.error(f"Error getting inventory movements: {e}")
            return []

    @classmethod
    def get_product_statistics(cls):
        """Get product statistics dashboard data"""
        try:
            conn, cursor = get_db()
            
            # Get basic counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_products,
                    COUNT(CASE WHEN quantity_in_stock <= min_stock_level THEN 1 END) as low_stock_count,
                    COUNT(CASE WHEN expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) 
                               AND expiry_date >= CURDATE() THEN 1 END) as expiring_soon_count,
                    SUM(CASE WHEN is_active = TRUE THEN quantity_in_stock * unit_price ELSE 0 END) as total_inventory_value
                FROM products
            """)
            
            stats = cursor.fetchone()
            cursor.close()
            
            return {
                'total_products': stats[0] or 0,
                'active_products': stats[1] or 0,
                'low_stock_count': stats[2] or 0,
                'expiring_soon_count': stats[3] or 0,
                'total_inventory_value': float(stats[4] or 0)
            }
            
        except Exception as e:
            logging.error(f"Error getting product statistics: {e}")
            return {
                'total_products': 0,
                'active_products': 0,
                'low_stock_count': 0,
                'expiring_soon_count': 0,
                'total_inventory_value': 0.0
            }

    def to_dict(self):
        """Convert product object to dictionary"""
        return {
            'id': self.id,
            'product_code': self.product_code,
            'barcode': self.barcode,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'category_id': self.category_id,
            'supplier_id': self.supplier_id,
            'brand': self.brand,
            'unit': self.unit,
            'unit_price': float(self.unit_price) if self.unit_price else 0.0,
            'cost_price': float(self.cost_price) if self.cost_price else 0.0,
            'mrp': float(self.mrp) if self.mrp else 0.0,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0.0,
            'discount_rate': float(self.discount_percentage) if self.discount_percentage else 0.0,  # Billing compatibility
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0.0,
            'quantity_in_stock': self.quantity_in_stock,
            'stock_quantity': self.quantity_in_stock,  # Billing compatibility
            'min_stock_level': self.min_stock_level,
            'max_stock_level': self.max_stock_level,
            'reorder_level': self.reorder_level,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'manufacturing_date': self.manufacturing_date.isoformat() if self.manufacturing_date else None,
            'batch_number': self.batch_number,
            'rack_location': self.rack_location,
            'weight_per_unit': float(self.weight_per_unit) if self.weight_per_unit else None,
            'dimensions': self.dimensions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Additional billing compatibility fields
            'price': float(self.unit_price) if self.unit_price else 0.0,
            'selling_price': self.get_discounted_price(),
            'final_price': self.get_final_price()
        }

    def __str__(self):
        return f"Product(id={self.id}, code='{self.product_code}', name='{self.name}', barcode='{self.barcode}', price={self.unit_price})"

    def __repr__(self):
        return self.__str__()

# TESTING UTILITIES


def test_product_operations():
    """Test product operations"""
    try:
        print("🔍 Testing Product model operations...")
        
        # Test 1: Create product
        test_product_data = {
            'name': 'Test Product',
            'unit_price': 25.50,
            'quantity_in_stock': 100,
            'category_id': 1,  
            'brand': 'Test Brand',
            'tax_rate': 18.0,
            'cost_price': 20.00,
            'description': 'This is a test product'
        }
        
        product_id = Product.create_product(**test_product_data)
        print(f"✅ Test 1 - Product created with ID: {product_id}")
        
        # Test 2: Get all products
        products = Product.get_all_products()
        print(f"✅ Test 2 - Retrieved {len(products)} products")
        
        # Test 3: Test billing compatibility
        if products:
            product = products[0]
            print(f"✅ Test 3 - Billing compatibility test:")
            print(f"   - discount_rate: {product.discount_rate}")
            print(f"   - price: {product.price}")
            print(f"   - discounted_price: {product.get_discounted_price()}")
            print(f"   - final_price: {product.get_final_price()}")
        
        # Test 4: Search products
        search_results = Product.search_products('Test')
        print(f"✅ Test 4 - Search found {len(search_results)} products")
        
        # Test 5: Update stock
        new_stock = Product.update_stock(product_id, 50, "Test stock update")
        print(f"✅ Test 5 - Stock updated to: {new_stock}")
        
        # Test 6: Get product by ID
        product = Product.get_product_by_id(product_id)
        print(f"✅ Test 6 - Retrieved product: {product.name if product else 'Not found'}")
        
        # Test 7: Test update_product_by_barcode method
        if product and product.barcode:
            Product.update_product_by_barcode(product.barcode, name="Updated Test Product")
            print(f"✅ Test 7 - Product updated by barcode successfully")
        else:
            print(f"⚠️ Test 7 - Skipped (no barcode available)")
        
        # Test 8: Test delete_product_by_barcode method
        if product and product.barcode:
            Product.delete_product_by_barcode(product.barcode)
            print(f"✅ Test 8 - Product deleted by barcode successfully")
        else:
            print(f"⚠️ Test 8 - Skipped (no barcode available)")
        
        print("✅ All Product model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Product model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run tests when file is executed directly
    test_product_operations()
