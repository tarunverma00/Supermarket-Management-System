"""
Supplier management model - FULLY UPDATED for complete UI compatibility
"""
from database import get_db
import logging

class Supplier:
    def __init__(self, id=None, supplier_code=None, name=None, contact_person=None, 
                 phone=None, email=None, address=None, city=None, state=None, 
                 pincode=None, gst_number=None, tax_id=None, payment_terms=None, 
                 credit_limit=0.0, outstanding_amount=0.0, is_active=True, 
                 created_at=None, updated_at=None):
        self.id = id
        self.supplier_code = supplier_code
        self.name = name
        self.contact_person = contact_person
        self.phone = phone
        self.email = email
        self.address = address
        self.city = city
        self.state = state
        self.pincode = pincode
        self.gst_number = gst_number
        self.tax_id = tax_id
        self.payment_terms = payment_terms
        self.credit_limit = credit_limit
        self.outstanding_amount = outstanding_amount
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create_supplier(cls, **kwargs):
        try:
            conn, cursor = get_db()
            
            # Extract required field
            name = kwargs.get('name')
            if not name:
                raise ValueError("Supplier name is required")
            
            # Check if supplier with this name already exists
            cursor.execute("SELECT id FROM suppliers WHERE name = %s", (name,))
            if cursor.fetchone():
                cursor.close()
                raise ValueError(f"Supplier with name '{name}' already exists")
            
            print(f"DEBUG: Creating supplier with data: {kwargs}")
            
            # Get all the fields that might be sent from UI
            supplier_code = kwargs.get('supplier_code')
            contact_person = kwargs.get('contact_person')
            phone = kwargs.get('phone')
            email = kwargs.get('email')
            address = kwargs.get('address')
            city = kwargs.get('city')
            state = kwargs.get('state')
            pincode = kwargs.get('pincode')
            gst_number = kwargs.get('gst_number')
            tax_id = kwargs.get('tax_id')
            payment_terms = kwargs.get('payment_terms', 'Net 30 Days')
            credit_limit = float(kwargs.get('credit_limit', 0.0))
            
            # First, check what columns actually exist in the suppliers table
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            print(f"DEBUG: Available columns in suppliers table: {columns}")
            
            # Build INSERT query based on available columns
            insert_columns = ['name']  # name is always required
            insert_values = [name]
            placeholders = ['%s']
            
            # Add optional columns if they exist in the table
            optional_fields = {
                'supplier_code': supplier_code,
                'contact_person': contact_person,
                'phone': phone,
                'email': email,
                'address': address,
                'city': city,
                'state': state,
                'pincode': pincode,
                'gst_number': gst_number,
                'tax_id': tax_id,
                'payment_terms': payment_terms,
                'credit_limit': credit_limit
            }
            
            for column, value in optional_fields.items():
                if column in columns and value is not None:
                    insert_columns.append(column)
                    insert_values.append(value)
                    placeholders.append('%s')
            
            # Add is_active if column exists
            if 'is_active' in columns:
                insert_columns.append('is_active')
                insert_values.append(True)
                placeholders.append('%s')
            
            # Build and execute the INSERT query
            query = f"""
                INSERT INTO suppliers ({', '.join(insert_columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            print(f"DEBUG: Executing query: {query}")
            print(f"DEBUG: With values: {insert_values}")
            
            cursor.execute(query, insert_values)
            supplier_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            
            logging.info(f"Supplier created successfully: {name} (ID: {supplier_id})")
            print(f"DEBUG: Supplier created with ID: {supplier_id}")
            
            return supplier_id
            
        except Exception as e:
            logging.error(f"Error creating supplier: {e}")
            print(f"DEBUG: Error creating supplier: {e}")
            if conn:
                conn.rollback()
            raise

    @classmethod
    def get_all_suppliers(cls):
        try:
            conn, cursor = get_db()
            
            # First check what columns actually exist
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            logging.debug(f"Available columns in suppliers table: {columns}")
            
            # Build query based on available columns
            base_columns = ['id', 'name']
            optional_columns = [
                'supplier_code', 'contact_person', 'phone', 'email', 'address', 
                'city', 'state', 'pincode', 'gst_number', 'tax_id', 'payment_terms', 
                'credit_limit', 'outstanding_amount', 'is_active', 'created_at', 'updated_at'
            ]
            
            select_columns = base_columns[:]
            for col in optional_columns:
                if col in columns:
                    select_columns.append(col)
            
            # Add WHERE clause for is_active if column exists
            where_clause = ""
            if 'is_active' in columns:
                where_clause = " WHERE is_active = TRUE"
            
            query = f"SELECT {', '.join(select_columns)} FROM suppliers{where_clause} ORDER BY name"
            cursor.execute(query)
            
            suppliers_data = cursor.fetchall()
            cursor.close()
            
            suppliers = []
            for data in suppliers_data:
                # Create supplier object with available data
                supplier_dict = {}
                for i, col in enumerate(select_columns):
                    if i < len(data):
                        supplier_dict[col] = data[i]
                
                supplier = cls(
                    id=supplier_dict.get('id'),
                    supplier_code=supplier_dict.get('supplier_code'),
                    name=supplier_dict.get('name'),
                    contact_person=supplier_dict.get('contact_person'),
                    phone=supplier_dict.get('phone'),
                    email=supplier_dict.get('email'),
                    address=supplier_dict.get('address'),
                    city=supplier_dict.get('city'),
                    state=supplier_dict.get('state'),
                    pincode=supplier_dict.get('pincode'),
                    gst_number=supplier_dict.get('gst_number'),
                    tax_id=supplier_dict.get('tax_id'),
                    payment_terms=supplier_dict.get('payment_terms'),
                    credit_limit=supplier_dict.get('credit_limit', 0.0),
                    outstanding_amount=supplier_dict.get('outstanding_amount', 0.0),
                    is_active=supplier_dict.get('is_active', True),
                    created_at=supplier_dict.get('created_at'),
                    updated_at=supplier_dict.get('updated_at')
                )
                suppliers.append(supplier)
            
            logging.info(f"Retrieved {len(suppliers)} suppliers from database")
            return suppliers
            
        except Exception as e:
            logging.error(f"Error getting suppliers: {e}")
            return []

    @classmethod
    def get_suppliers_simple(cls):
        """Simple method to get suppliers as list of tuples (id, name)"""
        try:
            conn, cursor = get_db()
            
            # Check if is_active column exists
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            
            where_clause = ""
            if 'is_active' in columns:
                where_clause = " WHERE is_active = TRUE"
            
            query = f"SELECT id, name FROM suppliers{where_clause} ORDER BY name"
            cursor.execute(query)
            suppliers_data = cursor.fetchall()
            cursor.close()
            
            logging.info(f"Retrieved {len(suppliers_data)} suppliers (simple)")
            return suppliers_data
            
        except Exception as e:
            logging.error(f"Error getting suppliers (simple): {e}")
            return []

    @classmethod
    def search_suppliers(cls, search_term):
        """Search suppliers by name or contact info"""
        try:
            conn, cursor = get_db()
            
            # Check available columns
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            
            # Build SELECT clause
            select_columns = ['id', 'name']
            optional_columns = [
                'supplier_code', 'contact_person', 'phone', 'email', 'address',
                'city', 'state', 'pincode', 'gst_number', 'tax_id', 'payment_terms',
                'credit_limit', 'outstanding_amount', 'is_active', 'created_at', 'updated_at'
            ]
            
            for col in optional_columns:
                if col in columns:
                    select_columns.append(col)
            
            # Build WHERE clause
            search_conditions = ["name LIKE %s"]
            search_params = [f"%{search_term}%"]
            
            if 'contact_person' in columns:
                search_conditions.append("COALESCE(contact_person, '') LIKE %s")
                search_params.append(f"%{search_term}%")
            
            if 'phone' in columns:
                search_conditions.append("COALESCE(phone, '') LIKE %s")
                search_params.append(f"%{search_term}%")
            
            where_clause = f"WHERE ({' OR '.join(search_conditions)})"
            
            # Add is_active filter if column exists
            if 'is_active' in columns:
                where_clause += " AND is_active = TRUE"
            
            query = f"SELECT {', '.join(select_columns)} FROM suppliers {where_clause} ORDER BY name"
            cursor.execute(query, search_params)
            
            suppliers_data = cursor.fetchall()
            cursor.close()
            
            suppliers = []
            for data in suppliers_data:
                supplier_dict = {}
                for i, col in enumerate(select_columns):
                    if i < len(data):
                        supplier_dict[col] = data[i]
                
                supplier = cls(
                    id=supplier_dict.get('id'),
                    supplier_code=supplier_dict.get('supplier_code'),
                    name=supplier_dict.get('name'),
                    contact_person=supplier_dict.get('contact_person'),
                    phone=supplier_dict.get('phone'),
                    email=supplier_dict.get('email'),
                    address=supplier_dict.get('address'),
                    city=supplier_dict.get('city'),
                    state=supplier_dict.get('state'),
                    pincode=supplier_dict.get('pincode'),
                    gst_number=supplier_dict.get('gst_number'),
                    tax_id=supplier_dict.get('tax_id'),
                    payment_terms=supplier_dict.get('payment_terms'),
                    credit_limit=supplier_dict.get('credit_limit', 0.0),
                    outstanding_amount=supplier_dict.get('outstanding_amount', 0.0),
                    is_active=supplier_dict.get('is_active', True),
                    created_at=supplier_dict.get('created_at'),
                    updated_at=supplier_dict.get('updated_at')
                )
                suppliers.append(supplier)
            
            return suppliers
            
        except Exception as e:
            logging.error(f"Error searching suppliers: {e}")
            return []

    @classmethod
    def get_supplier_by_id(cls, supplier_id):
        """Get supplier by ID"""
        try:
            conn, cursor = get_db()
            
            # Check available columns
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            
            select_columns = ['id', 'name']
            optional_columns = [
                'supplier_code', 'contact_person', 'phone', 'email', 'address',
                'city', 'state', 'pincode', 'gst_number', 'tax_id', 'payment_terms',
                'credit_limit', 'outstanding_amount', 'is_active', 'created_at', 'updated_at'
            ]
            
            for col in optional_columns:
                if col in columns:
                    select_columns.append(col)
            
            where_clause = "WHERE id = %s"
            params = [supplier_id]
            
            if 'is_active' in columns:
                where_clause += " AND is_active = TRUE"
            
            query = f"SELECT {', '.join(select_columns)} FROM suppliers {where_clause}"
            cursor.execute(query, params)
            
            supplier_data = cursor.fetchone()
            cursor.close()
            
            if supplier_data:
                supplier_dict = {}
                for i, col in enumerate(select_columns):
                    if i < len(supplier_data):
                        supplier_dict[col] = supplier_data[i]
                
                return cls(
                    id=supplier_dict.get('id'),
                    supplier_code=supplier_dict.get('supplier_code'),
                    name=supplier_dict.get('name'),
                    contact_person=supplier_dict.get('contact_person'),
                    phone=supplier_dict.get('phone'),
                    email=supplier_dict.get('email'),
                    address=supplier_dict.get('address'),
                    city=supplier_dict.get('city'),
                    state=supplier_dict.get('state'),
                    pincode=supplier_dict.get('pincode'),
                    gst_number=supplier_dict.get('gst_number'),
                    tax_id=supplier_dict.get('tax_id'),
                    payment_terms=supplier_dict.get('payment_terms'),
                    credit_limit=supplier_dict.get('credit_limit', 0.0),
                    outstanding_amount=supplier_dict.get('outstanding_amount', 0.0),
                    is_active=supplier_dict.get('is_active', True),
                    created_at=supplier_dict.get('created_at'),
                    updated_at=supplier_dict.get('updated_at')
                )
            return None
            
        except Exception as e:
            logging.error(f"Error getting supplier by ID: {e}")
            return None

    @classmethod
    def update_supplier(cls, supplier_id, **kwargs):
        """Update supplier information"""
        try:
            conn, cursor = get_db()
            
            # Check available columns
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            
            set_clauses = []
            values = []
            
            valid_fields = [
                'supplier_code', 'name', 'contact_person', 'phone', 'email', 'address',
                'city', 'state', 'pincode', 'gst_number', 'tax_id', 'payment_terms', 'credit_limit'
            ]
            
            for field, value in kwargs.items():
                if field in valid_fields and field in columns:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                cursor.close()
                raise ValueError("No valid fields to update")
            
            # Add updated_at if column exists
            if 'updated_at' in columns:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            
            values.append(supplier_id)
            query = f"UPDATE suppliers SET {', '.join(set_clauses)} WHERE id = %s"
            
            cursor.execute(query, values)
            affected_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            
            if affected_rows == 0:
                raise ValueError(f"No supplier found with ID {supplier_id}")
            
            logging.info(f"Supplier updated successfully: ID {supplier_id}")
            
        except Exception as e:
            logging.error(f"Error updating supplier: {e}")
            if conn:
                conn.rollback()
            raise

    @classmethod
    def delete_supplier(cls, supplier_id):
        """Delete supplier (soft delete if is_active exists, hard delete otherwise)"""
        try:
            conn, cursor = get_db()
            
            # Check if is_active column exists
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            
            # Check if supplier exists
            cursor.execute("SELECT name FROM suppliers WHERE id = %s", (supplier_id,))
            supplier = cursor.fetchone()
            if not supplier:
                cursor.close()
                raise ValueError(f"No supplier found with ID {supplier_id}")
            
            if 'is_active' in columns:
                # Soft delete
                cursor.execute("UPDATE suppliers SET is_active = FALSE WHERE id = %s", (supplier_id,))
                action = "deactivated"
            else:
                # Hard delete
                cursor.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
                action = "deleted"
            
            conn.commit()
            cursor.close()
            
            logging.info(f"Supplier {action} successfully: {supplier[0]} (ID: {supplier_id})")
            
        except Exception as e:
            logging.error(f"Error deleting supplier: {e}")
            if conn:
                conn.rollback()
            raise

    @classmethod
    def get_supplier_count(cls):
        """Get total number of active suppliers"""
        try:
            conn, cursor = get_db()
            
            # Check if is_active column exists
            cursor.execute("DESCRIBE suppliers")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'is_active' in columns:
                cursor.execute("SELECT COUNT(*) FROM suppliers WHERE is_active = TRUE")
            else:
                cursor.execute("SELECT COUNT(*) FROM suppliers")
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count
            
        except Exception as e:
            logging.error(f"Error getting supplier count: {e}")
            return 0

    def to_dict(self):
        """Convert supplier object to dictionary"""
        return {
            'id': self.id,
            'supplier_code': self.supplier_code,
            'name': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'gst_number': self.gst_number,
            'tax_id': self.tax_id,
            'payment_terms': self.payment_terms,
            'credit_limit': self.credit_limit,
            'outstanding_amount': self.outstanding_amount,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __str__(self):
        return f"Supplier(id={self.id}, name='{self.name}', supplier_code='{self.supplier_code}')"

    def __repr__(self):
        return self.__str__()
