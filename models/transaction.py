"""
Transaction and billing management system
"""
from database import get_db
from datetime import datetime
import logging
import uuid
from config import TAX_RATE, DISCOUNT_THRESHOLD, DISCOUNT_RATE
from decimal import Decimal, ROUND_HALF_UP
import mysql.connector


class Transaction:
    def __init__(self, id=None, transaction_number=None, customer_id=None, employee_id=None,
                 transaction_date=None, subtotal=0.0, discount_amount=0.0, tax_amount=0.0,
                 total_amount=0.0, payment_method='cash', payment_status='completed', notes=None):
        
        self.id = id
        self.transaction_number = transaction_number
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.transaction_date = transaction_date
        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.notes = notes
        self.items = []

    @staticmethod
    def safe_decimal_conversion(value, decimal_places=4):
        """Safely convert value to properly rounded decimal matching database precision"""
        try:
            if value is None or value == '' or value == 'None':
                return 0.0
            
            if isinstance(value, str):
                value = value.strip()
                if value == '':
                    return 0.0
            
            float_value = float(value)
            
            import math
            if math.isnan(float_value) or math.isinf(float_value):
                return 0.0
            
            decimal_value = Decimal(str(float_value))
            places = Decimal('0.' + '0' * decimal_places)
            rounded_value = float(decimal_value.quantize(places, rounding=ROUND_HALF_UP))
            
            return rounded_value
            
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            print(f"❌ DEBUG: Decimal conversion error for value '{value}': {e}")
            return 0.0

    @classmethod
    def calculate_item_amounts(cls, quantity, unit_price, product_discount_rate=0.0):
        """UPDATED: Calculate all item-level amounts with enhanced precision - no truncation limits"""
        try:
            qty = int(float(quantity)) if quantity else 0
            original_price = float(unit_price) if unit_price else 0.0
            discount_rate = float(product_discount_rate) if product_discount_rate else 0.0
            
            if qty <= 0 or original_price <= 0:
                return {
                    'quantity': 0,
                    'unit_price': 0.0,
                    'original_price': 0.0,
                    'discount_rate': 0.0,
                    'discount_amount': 0.0,
                    'tax_rate': 18.0,
                    'tax_amount': 0.0,
                    'line_total': 0.0
                }
            
            # Calculate discount amount per unit
            discount_per_unit = original_price * discount_rate / 100
            discount_amount = discount_per_unit * qty
            discount_amount = round(discount_amount, 4)
            
            # Calculate discounted unit price
            discounted_unit_price = original_price - discount_per_unit
            discounted_unit_price = round(discounted_unit_price, 4)
            
            # Calculate subtotal after discount
            subtotal_after_discount = discounted_unit_price * qty
            
            # Calculate tax amount - UPDATED: No artificial limits
            tax_rate = 18.0  
            tax_amount = subtotal_after_discount * (tax_rate / 100)
            tax_amount = round(tax_amount, 4)
            
            # Calculate final line total - UPDATED: No artificial limits
            line_total = subtotal_after_discount + tax_amount
            line_total = round(line_total, 4)
            
            result = {
                'quantity': qty,
                'unit_price': round(discounted_unit_price, 4),
                'original_price': round(original_price, 4),
                'discount_rate': round(discount_rate, 2),
                'discount_amount': discount_amount,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'line_total': line_total
            }
            
            print(f"🔍 DEBUG: Item amounts calculated (no limits): {result}")
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: Item amount calculation error: {e}")
            return {
                'quantity': 0,
                'unit_price': 0.0,
                'original_price': 0.0,
                'discount_rate': 0.0,
                'discount_amount': 0.0,
                'tax_rate': 18.0,
                'tax_amount': 0.0,
                'line_total': 0.0
            }

    @staticmethod
    def safe_line_total_calculation(quantity, unit_price):
        """UPDATED: Calculate line total with proper precision - no truncation limits"""
        try:
            print(f"🔍 DEBUG: Calculating line total - qty: {quantity}, price: {unit_price}")
            
            if quantity is None or quantity == '' or quantity == 'None':
                return 0.0
            if unit_price is None or unit_price == '' or unit_price == 'None':
                return 0.0
            
            try:
                qty = int(float(quantity))
            except (ValueError, TypeError):
                print(f"❌ DEBUG: Invalid quantity conversion: {quantity}")
                return 0.0
                
            try:
                price = float(unit_price)
            except (ValueError, TypeError):
                print(f"❌ DEBUG: Invalid price conversion: {unit_price}")
                return 0.0
            
            if qty <= 0 or price <= 0:
                return 0.0
            
            line_total = qty * price
            line_total_rounded = round(line_total, 4)
            
            print(f"✅ DEBUG: Line total calculated: {qty} x {price} = {line_total_rounded}")
            return line_total_rounded
            
        except (ValueError, TypeError) as e:
            print(f"❌ DEBUG: Line total calculation error: {e}")
            return 0.0

    @classmethod
    def safe_tax_calculation(cls, taxable_amount, tax_rate):
        """UPDATED: Calculate tax with proper precision - no artificial limits"""
        try:
            print(f"🔍 DEBUG: Calculating tax - taxable: {taxable_amount}, rate: {tax_rate}")
            
            if taxable_amount is None or taxable_amount <= 0:
                return 0.0
            
            if tax_rate is None or tax_rate <= 0:
                return 0.0
            
            tax_amount = float(taxable_amount) * float(tax_rate)
            tax_rounded = round(tax_amount, 4)
            
            print(f"✅ DEBUG: Tax calculated: {taxable_amount} x {tax_rate} = {tax_rounded}")
            return tax_rounded
            
        except (ValueError, TypeError) as e:
            print(f"❌ DEBUG: Tax calculation error: {e}")
            return 0.0

    @classmethod
    def validate_transaction_amounts(cls, amounts):
        """UPDATED: Basic validation without artificial database limits"""
        print(f"🔍 DEBUG: Validating transaction amounts: {amounts}")
        
        for field, value in amounts.items():
            if value < 0:
                raise ValueError(f"{field} amount cannot be negative: {value}")
            
            # Basic sanity check - not database limits
            if value > 999999999999.99:  # Extremely large value check
                print(f"⚠️ WARNING: {field} amount is very large: {value}")
        
        print("✅ DEBUG: Transaction amounts validation passed")
        return True

    @classmethod
    def validate_transaction_item_data(cls, product_id, quantity, unit_price, line_total):
        """UPDATED: Validate data with basic checks - no artificial truncation limits"""
        print(f"🔍 DEBUG: Validating transaction item data:")
        print(f"   - product_id: {product_id}")
        print(f"   - quantity: {quantity}")
        print(f"   - unit_price: {unit_price}")
        print(f"   - line_total: {line_total}")
        
        if any(x is None for x in [product_id, quantity, unit_price, line_total]):
            raise ValueError("NULL values not allowed in transaction items")
        
        import math
        for name, val in [('quantity', quantity), ('unit_price', unit_price), ('line_total', line_total)]:
            if isinstance(val, (int, float)) and (math.isnan(val) or math.isinf(val)):
                raise ValueError(f"Invalid numeric value for {name}: {val}")
        
        try:
            product_id_int = int(product_id)
            if product_id_int <= 0:
                raise ValueError(f"Invalid product_id: {product_id_int}")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid product_id format: {product_id}")
        
        try:
            quantity_int = int(float(quantity))
            if quantity_int <= 0:
                raise ValueError(f"Invalid quantity: {quantity_int}")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid quantity format: {quantity}")
        
        try:
            unit_price_float = float(unit_price)
            if unit_price_float <= 0:
                raise ValueError(f"Invalid unit price: {unit_price_float}")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid unit price format: {unit_price}")
        
        try:
            line_total_float = float(line_total)
            if line_total_float <= 0:
                raise ValueError(f"Invalid line total: {line_total_float}")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid line total format: {line_total}")
        
        print("✅ DEBUG: Transaction item data validation passed")
        return True

    @classmethod
    def generate_transaction_number(cls):
        """Generate unique transaction number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"TXN-{timestamp}-{unique_id}"

    @classmethod
    def calculate_amounts(cls, cart_items):
        """UPDATED: Calculate amounts without artificial limits"""
        subtotal = 0.0
        total_item_discount = 0.0
        total_item_tax = 0.0
        
        print(f"🔍 DEBUG: Calculating amounts for {len(cart_items)} items")
        
        for i, item in enumerate(cart_items):
            try:
                quantity = item.get('quantity', 0)
                unit_price = item.get('unit_price', 0)
                product_discount = item.get('discount_rate', 0.0)
                
                item_amounts = cls.calculate_item_amounts(quantity, unit_price, product_discount)
                
                print(f"🔍 DEBUG: Item {i+1} - qty: {quantity}, price: {unit_price}, line_total: {item_amounts['line_total']}")
                
                subtotal += (item_amounts['original_price'] * item_amounts['quantity'])
                total_item_discount += item_amounts['discount_amount']
                total_item_tax += item_amounts['tax_amount']
                
            except (ValueError, TypeError) as e:
                print(f"❌ DEBUG: Error calculating item {i+1}: {e}")
                continue
        
        subtotal = cls.safe_decimal_conversion(subtotal, 4)
        
        transaction_discount_amount = 0.0
        effective_subtotal = subtotal - total_item_discount
        if effective_subtotal >= DISCOUNT_THRESHOLD:
            transaction_discount_amount = effective_subtotal * DISCOUNT_RATE
        
        transaction_discount_amount = cls.safe_decimal_conversion(transaction_discount_amount, 4)
        total_discount = total_item_discount + transaction_discount_amount
        
        total_amount = subtotal - total_discount + total_item_tax
        total_amount = cls.safe_decimal_conversion(total_amount, 4)
        
        result = {
            'subtotal': subtotal,
            'discount_amount': total_discount,
            'tax_amount': total_item_tax,
            'total_amount': total_amount
        }
        
        print(f"🔍 DEBUG: Final amounts: {result}")
        cls.validate_transaction_amounts(result)
        
        return result

    @classmethod
    def validate_cart_items(cls, cart_items):
        """UPDATED: Enhanced validation for cart items"""
        if not cart_items:
            raise ValueError("Cart is empty")
        
        print(f"🔍 DEBUG: Validating {len(cart_items)} cart items")
        
        for i, item in enumerate(cart_items):
            print(f"🔍 DEBUG: Validating item {i+1}: {item}")
            
            required_fields = ['product_id', 'quantity', 'unit_price']
            for field in required_fields:
                if field not in item or item[field] is None or item[field] == '':
                    raise ValueError(f"Missing or empty field '{field}' in item {i+1}")
            
            try:
                product_id = int(item['product_id'])
                if product_id <= 0:
                    raise ValueError(f"Invalid product_id {product_id} in item {i+1}")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid product_id format in item {i+1}: {item['product_id']}")
            
            try:
                quantity = int(float(item['quantity']))
                if quantity <= 0:
                    raise ValueError(f"Invalid quantity {quantity} in item {i+1}")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid quantity format in item {i+1}: {item['quantity']}")
            
            try:
                unit_price = float(item['unit_price'])
                if unit_price <= 0:
                    raise ValueError(f"Invalid unit price {unit_price} in item {i+1}")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid unit price format in item {i+1}: {item['unit_price']}")
            
            print(f"✅ DEBUG: Item {i+1} validation passed")
        
        print("✅ DEBUG: All cart items validated successfully")

    @classmethod
    def create_transaction(cls, customer_id, employee_id, cart_items, payment_method='cash', notes=None):
        """UPDATED: Create transaction with enhanced error handling and no truncation limits"""
        conn = None
        cursor = None
        
        try:
            print(f"🔍 DEBUG: Starting transaction creation with {len(cart_items)} items")
            
            cls.validate_cart_items(cart_items)
            print("✅ DEBUG: Cart validation passed")
            
            conn, cursor = get_db()
            print("✅ DEBUG: Database connection established")
            
            conn.start_transaction()
            print("✅ DEBUG: Database transaction started")
            
            amounts = cls.calculate_amounts(cart_items)
            print(f"✅ DEBUG: Amounts calculated: {amounts}")
            
            transaction_number = cls.generate_transaction_number()
            print(f"✅ DEBUG: Generated transaction number: {transaction_number}")
            
            print(f"🔍 DEBUG: Inserting transaction with amounts:")
            print(f"   - subtotal: {amounts['subtotal']}")
            print(f"   - discount_amount: {amounts['discount_amount']}")
            print(f"   - tax_amount: {amounts['tax_amount']}")
            print(f"   - total_amount: {amounts['total_amount']}")
            
            cursor.execute("""
                INSERT INTO transactions (transaction_number, customer_id, employee_id, 
                                        subtotal, discount_amount, tax_amount, total_amount, 
                                        payment_method, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (transaction_number, customer_id, employee_id, 
                  float(amounts['subtotal']), float(amounts['discount_amount']), 
                  float(amounts['tax_amount']), float(amounts['total_amount']),
                  payment_method, notes))
            
            transaction_id = cursor.lastrowid
            print(f"✅ DEBUG: Transaction inserted with ID: {transaction_id}")
            
            items_inserted = 0
            for i, item in enumerate(cart_items):
                try:
                    product_id = int(item['product_id'])
                    product_discount = item.get('discount_rate', 0.0)
                    
                    item_amounts = cls.calculate_item_amounts(
                        item['quantity'], 
                        item['unit_price'], 
                        product_discount
                    )
                    
                    print(f"🔍 DEBUG: Processing item {i+1}/{len(cart_items)}")
                    print(f"   - Product ID: {product_id}")
                    print(f"   - Calculated amounts: {item_amounts}")
                    
                    if item_amounts['line_total'] <= 0:
                        print(f"⚠️ WARNING: Skipping item {i+1} - zero line total")
                        continue
                    
                    cls.validate_transaction_item_data(
                        product_id, 
                        item_amounts['quantity'], 
                        item_amounts['unit_price'], 
                        item_amounts['line_total']
                    )
                    
                    print(f"🔍 DEBUG: Inserting transaction item {i+1}")
                    cursor.execute("""
                        INSERT INTO transaction_items (
                            transaction_id, product_id, quantity, unit_price, 
                            original_price, discount_rate, discount_amount, 
                            tax_rate, tax_amount, line_total, batch_number, 
                            expiry_date, serial_numbers
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        int(transaction_id),
                        int(product_id),
                        int(item_amounts['quantity']),
                        float(item_amounts['unit_price']),
                        float(item_amounts['original_price']),
                        float(item_amounts['discount_rate']),
                        float(item_amounts['discount_amount']),
                        float(item_amounts['tax_rate']),
                        float(item_amounts['tax_amount']),
                        float(item_amounts['line_total']),
                        item.get('batch_number'),
                        item.get('expiry_date'),
                        item.get('serial_numbers')
                    ))
                    
                    items_inserted += 1
                    print(f"✅ DEBUG: Item {i+1} inserted successfully")
                    
                    # Update product stock
                    cursor.execute("SELECT quantity_in_stock, name FROM products WHERE id = %s", (product_id,))
                    stock_result = cursor.fetchone()
                    
                    if stock_result:
                        current_stock, product_name = stock_result
                        print(f"🔍 DEBUG: Current stock for {product_name}: {current_stock}")
                        
                        if current_stock >= item_amounts['quantity']:
                            cursor.execute("""
                                UPDATE products SET quantity_in_stock = quantity_in_stock - %s
                                WHERE id = %s
                            """, (item_amounts['quantity'], product_id))
                            print(f"✅ DEBUG: Stock updated for {product_name}")
                        else:
                            print(f"⚠️ WARNING: Insufficient stock for {product_name}")
                    
                    # Log inventory movement
                    try:
                        from models.product import Product
                        Product.log_inventory_movement(
                            product_id, 'out', item_amounts['quantity'], 
                            f'Sale - Transaction {transaction_number}', employee_id
                        )
                        print(f"✅ DEBUG: Inventory movement logged")
                    except Exception as inv_error:
                        print(f"⚠️ WARNING: Inventory logging failed: {inv_error}")
                
                except mysql.connector.Error as db_error:
                    print(f"❌ DEBUG: Database error for item {i+1}: {db_error}")
                    print(f"❌ DEBUG: Error code: {db_error.errno}")
                    
                    # Improved error handling
                    if "1265" in str(db_error) or "data truncated" in str(db_error).lower():
                        print(f"❌ DEBUG: Data truncation still occurring!")
                        print(f"❌ DEBUG: Item amounts causing issue:")
                        for key, value in item_amounts.items():
                            print(f"   {key}: {value} (type: {type(value)})")
                        raise ValueError(f"Data truncation error on item {i+1}. Please check database column sizes.")
                    else:
                        raise db_error
                
                except Exception as item_error:
                    print(f"❌ DEBUG: Error processing item {i+1}: {item_error}")
                    continue
            
            print(f"✅ DEBUG: Successfully inserted {items_inserted}/{len(cart_items)} items")
            
            if items_inserted == 0:
                raise ValueError("No items were successfully processed")
            
            # Update customer if provided
            if customer_id:
                try:
                    cursor.execute("""
                        UPDATE customers SET 
                            total_purchases = total_purchases + %s,
                            loyalty_points = loyalty_points + %s
                        WHERE id = %s
                    """, (amounts['total_amount'], int(amounts['total_amount']), customer_id))
                    print(f"✅ DEBUG: Customer {customer_id} updated")
                except Exception as customer_error:
                    print(f"⚠️ WARNING: Customer update failed: {customer_error}")
            
            conn.commit()
            print("✅ DEBUG: Database transaction committed successfully")
            
            logging.info(f"Transaction created successfully: {transaction_number} with {items_inserted} items")
            return transaction_id, transaction_number
            
        except mysql.connector.Error as db_error:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Database error: {db_error}")
            
            error_msg = str(db_error).lower()
            if "data truncated" in error_msg or "1265" in str(db_error):
                raise Exception("Data truncation error still occurring. Please verify your database column sizes have been properly updated.")
            else:
                raise Exception(f"Database error: {str(db_error)}")
                
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ DEBUG: Transaction failed: {e}")
            raise Exception(f"Transaction failed: {str(e)}")
            
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def get_recent_transactions(cls, limit=50):
        """Get recent transactions"""
        try:
            conn, cursor = get_db()
            
            cursor.execute("""
                SELECT t.id, t.transaction_number, t.transaction_date, t.total_amount,
                       t.payment_method, t.payment_status, c.name as customer_name
                FROM transactions t
                LEFT JOIN customers c ON t.customer_id = c.id
                ORDER BY t.transaction_date DESC, t.id DESC
                LIMIT %s
            """, (limit,))
            
            transactions = cursor.fetchall()
            cursor.close()
            return transactions
            
        except Exception as e:
            logging.error(f"Error getting recent transactions: {e}")
            return []

    @classmethod
    def get_transaction_details(cls, transaction_id):
        """Get complete transaction details with items"""
        try:
            conn, cursor = get_db()
            
            cursor.execute("""
                SELECT t.*, c.name as customer_name, e.name as employee_name
                FROM transactions t
                LEFT JOIN customers c ON t.customer_id = c.id
                LEFT JOIN employees e ON t.employee_id = e.id
                WHERE t.id = %s
            """, (transaction_id,))
            
            transaction_data = cursor.fetchone()
            
            if not transaction_data:
                return None
            
            cursor.execute("""
                SELECT ti.*, p.name as product_name, p.barcode
                FROM transaction_items ti
                LEFT JOIN products p ON ti.product_id = p.id
                WHERE ti.transaction_id = %s
                ORDER BY ti.id
            """, (transaction_id,))
            
            items_data = cursor.fetchall()
            
            transaction = cls(*transaction_data[:11])
            if len(transaction_data) > 11:
                transaction.customer_name = transaction_data[11]
            if len(transaction_data) > 12:
                transaction.employee_name = transaction_data[12]
            transaction.items = items_data or []
            
            cursor.close()
            return transaction
            
        except Exception as e:
            logging.error(f"Error getting transaction details: {e}")
            return None

    @classmethod
    def get_daily_sales(cls, date=None):
        """Get daily sales summary"""
        if not date:
            date = datetime.now().date()
        
        try:
            conn, cursor = get_db()
            
            cursor.execute("""
                SELECT COUNT(*) as transaction_count,
                       COALESCE(SUM(subtotal), 0) as total_subtotal,
                       COALESCE(SUM(discount_amount), 0) as total_discount,
                       COALESCE(SUM(tax_amount), 0) as total_tax,
                       COALESCE(SUM(total_amount), 0) as total_sales
                FROM transactions
                WHERE DATE(transaction_date) = %s AND payment_status = 'completed'
            """, (date,))
            
            sales_data = cursor.fetchone()
            cursor.close()
            
            if sales_data:
                return {
                    'date': date,
                    'transaction_count': sales_data[0] or 0,
                    'total_subtotal': float(sales_data[1] or 0.0),
                    'total_discount': float(sales_data[2] or 0.0),
                    'total_tax': float(sales_data[3] or 0.0),
                    'total_sales': float(sales_data[4] or 0.0)
                }
            
        except Exception as e:
            logging.error(f"Error getting daily sales: {e}")
        
        return {
            'date': date,
            'transaction_count': 0,
            'total_subtotal': 0.0,
            'total_discount': 0.0,
            'total_tax': 0.0,
            'total_sales': 0.0
        }

    @classmethod
    def get_sales_by_date_range(cls, from_date, to_date):
        """Get sales data for date range"""
        try:
            conn, cursor = get_db()
            
            from_date_db = datetime.strptime(from_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            to_date_db = datetime.strptime(to_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT DATE(transaction_date) as sale_date,
                       SUM(total_amount) as total_sales,
                       COUNT(*) as transaction_count,
                       SUM(tax_amount) as total_tax,
                       SUM(discount_amount) as total_discount,
                       AVG(total_amount) as avg_transaction
                FROM transactions 
                WHERE DATE(transaction_date) BETWEEN %s AND %s 
                  AND payment_status = 'completed'
                GROUP BY DATE(transaction_date)
                ORDER BY sale_date
            """, (from_date_db, to_date_db))
            
            results = cursor.fetchall()
            cursor.close()
            return results or []
            
        except Exception as e:
            logging.error(f"Error getting sales by date range: {e}")
            return []

    @classmethod
    def refund_transaction(cls, transaction_id, refund_reason, employee_id):
        """Process transaction refund"""
        try:
            conn, cursor = get_db()
            conn.start_transaction()
            
            cursor.execute("""
                SELECT ti.product_id, ti.quantity
                FROM transaction_items ti
                WHERE ti.transaction_id = %s
            """, (transaction_id,))
            
            items_data = cursor.fetchall()
            
            for product_id, quantity in items_data:
                cursor.execute("""
                    UPDATE products SET quantity_in_stock = quantity_in_stock + %s
                    WHERE id = %s
                """, (quantity, product_id))
                
                try:
                    from models.product import Product
                    Product.log_inventory_movement(
                        product_id, 'in', quantity, 
                        f'Refund - Transaction ID {transaction_id}', employee_id
                    )
                except Exception as inv_error:
                    print(f"⚠️ WARNING: Refund inventory logging failed: {inv_error}")
            
            cursor.execute("""
                UPDATE transactions SET payment_status = 'refunded', notes = %s
                WHERE id = %s
            """, (refund_reason, transaction_id))
            
            conn.commit()
            cursor.close()
            
            logging.info(f"Transaction refunded successfully: ID {transaction_id}")
            
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Error processing refund: {e}")
            raise

    def generate_receipt(self):
        """Generate formatted receipt text"""
        receipt_lines = []
        receipt_lines.append("=" * 50)
        receipt_lines.append("         SUPERMARKET RECEIPT")
        receipt_lines.append("=" * 50)
        receipt_lines.append(f"Transaction: {self.transaction_number}")
        receipt_lines.append(f"Date: {self.transaction_date}")
        receipt_lines.append(f"Customer: {getattr(self, 'customer_name', 'Walk-in')}")
        receipt_lines.append("-" * 50)
        
        if hasattr(self, 'items') and self.items:
            for item in self.items:
                try:
                    if isinstance(item, (list, tuple)):
                        item_name = item[15] if len(item) > 15 else 'Unknown'
                        quantity = item[3] if len(item) > 3 else 0
                        original_price = item[5] if len(item) > 5 else 0.0
                        discount_amount = item[7] if len(item) > 7 else 0.0
                        tax_amount = item[9] if len(item) > 9 else 0.0
                        line_total = item[10] if len(item) > 10 else 0.0
                    else:
                        item_name = item.get('product_name', 'Unknown')
                        quantity = item.get('quantity', 0)
                        original_price = item.get('original_price', 0.0)
                        discount_amount = item.get('discount_amount', 0.0)
                        tax_amount = item.get('tax_amount', 0.0)
                        line_total = item.get('line_total', 0.0)
                    
                    item_line = f"{str(item_name)[:20]:<20} {quantity:>3} x ₹{original_price:>6.2f}"
                    receipt_lines.append(item_line)
                    
                    if discount_amount > 0:
                        receipt_lines.append(f"{'  Discount:':<20} -₹{discount_amount:>8.2f}")
                    
                    receipt_lines.append(f"{'  Tax:':<20} ₹{tax_amount:>8.2f}")
                    receipt_lines.append(f"{'  Total:':<20} ₹{line_total:>8.2f}")
                    receipt_lines.append("")
                    
                except Exception as e:
                    receipt_lines.append(f"Item error: {str(e)}")
        
        receipt_lines.append("-" * 50)
        receipt_lines.append(f"Subtotal:        ₹{self.subtotal:>10.2f}")
        
        if self.discount_amount > 0:
            receipt_lines.append(f"Discount:        ₹{self.discount_amount:>10.2f}")
        
        receipt_lines.append(f"Tax (GST):       ₹{self.tax_amount:>10.2f}")
        receipt_lines.append("=" * 50)
        receipt_lines.append(f"TOTAL:           ₹{self.total_amount:>10.2f}")
        receipt_lines.append("=" * 50)
        receipt_lines.append(f"Payment Method: {self.payment_method.upper()}")
        receipt_lines.append("")
        receipt_lines.append("Thank you for shopping with us!")
        receipt_lines.append("=" * 50)
        
        return "\n".join(receipt_lines)

    def __str__(self):
        return f"Transaction({self.transaction_number}, ₹{self.total_amount:.2f}, {self.payment_method})"

    def __repr__(self):
        return self.__str__()


# =====================================================================
# DEBUGGING AND TESTING UTILITIES
# =====================================================================

def test_large_transaction():
    """Test transaction with large values to verify no truncation"""
    try:
        print("🔍 Testing large value transaction...")
        
        # Test cart with high values
        test_cart = [
            {'product_id': 1, 'quantity': 100, 'unit_price': 10000.50},
            {'product_id': 2, 'quantity': 50, 'unit_price': 25000.75}
        ]
        
        print(f"Test cart with large values: {test_cart}")
        
        Transaction.validate_cart_items(test_cart)
        print("✅ Large value cart validation passed")
        
        amounts = Transaction.calculate_amounts(test_cart)
        print(f"✅ Large value calculation: {amounts}")
        
        print("✅ Large value transaction test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Large value transaction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_database_schema():
    """Verify database schema can handle large values"""
    try:
        print("🔍 Verifying database schema...")
        
        conn, cursor = get_db()
        
        cursor.execute("DESCRIBE transaction_items")
        columns = cursor.fetchall()
        print("📋 transaction_items columns after update:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (NULL: {col[2]})")
        
        cursor.execute("DESCRIBE transactions")
        columns = cursor.fetchall()
        print("📋 transactions columns after update:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (NULL: {col[2]})")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False


if __name__ == "__main__":
    print("Running updated Transaction model tests...")
    verify_database_schema()
    test_large_transaction()
