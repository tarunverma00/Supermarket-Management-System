"""
User model for authentication and user management
"""
import hashlib
import os
import logging
from datetime import datetime
from database import get_db

class User:
    def __init__(self, id=None, username=None, email=None, phone=None, role=None, is_active=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.phone = phone
        self.role = role
        self.is_active = is_active
        self.created_at = created_at
    
    @staticmethod
    def generate_salt():
        """Generate random salt for password hashing"""
        return os.urandom(32).hex()
    
    @staticmethod
    def hash_password(password, salt):
        """Hash password with salt using SHA-256"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @classmethod
    def create_user(cls, username, password, role, email=None, phone=None):
        """Create a new user"""
        try:
            conn, cursor = get_db()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                raise ValueError("Username already exists")
            
            # Generate salt and hash password
            salt = cls.generate_salt()
            hashed_password = cls.hash_password(password, salt)
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, password, salt, role, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, salt, role, email, phone))
            
            user_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            
            # Log the action
            cls.log_action(user_id, "User created", {"username": username, "role": role})
            logging.info(f"User created successfully: {username}")
            
            return user_id
            
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            raise
    
    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user credentials"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                SELECT id, username, password, salt, role, email, phone, is_active
                FROM users WHERE username = %s
            """, (username,))
            
            user_data = cursor.fetchone()
            cursor.close()
            
            if not user_data:
                return None, "User not found"
            
            user_id, db_username, db_password, salt, role, email, phone, is_active = user_data
            
            if not is_active:
                return None, "Account is disabled"
            
            # Verify password
            hashed_input = cls.hash_password(password, salt)
            if hashed_input == db_password:
                user = cls(user_id, db_username, email, phone, role, is_active)
                cls.log_action(user_id, "User login", {"username": username})
                logging.info(f"User authenticated successfully: {username}")
                return user, "Success"
            else:
                cls.log_action(None, "Failed login attempt", {"username": username})
                return None, "Invalid password"
                
        except Exception as e:
            logging.error(f"Error during authentication: {e}")
            return None, "Authentication error"
    
    @classmethod
    def get_user_by_id(cls, user_id):
        """Get user by ID"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                SELECT id, username, role, email, phone, is_active, created_at
                FROM users WHERE id = %s
            """, (user_id,))
            
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return cls(*user_data)
            return None
            
        except Exception as e:
            logging.error(f"Error getting user by ID: {e}")
            return None
    
    @classmethod
    def get_all_users(cls):
        """Get all users"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                SELECT id, username, role, email, phone, is_active, created_at
                FROM users ORDER BY created_at DESC
            """)
            
            users_data = cursor.fetchall()
            cursor.close()
            
            return [cls(*user_data) for user_data in users_data]
            
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []
    
    @classmethod
    def update_user(cls, user_id, **kwargs):
        """Update user information"""
        try:
            conn, cursor = get_db()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for field, value in kwargs.items():
                if field in ['username', 'email', 'phone', 'role', 'is_active']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                raise ValueError("No valid fields to update")
            
            values.append(user_id)
            
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
            cursor.execute(query, values)
            
            conn.commit()
            cursor.close()
            
            cls.log_action(user_id, "User updated", kwargs)
            logging.info(f"User updated successfully: ID {user_id}")
            
        except Exception as e:
            logging.error(f"Error updating user: {e}")
            raise
    
    @classmethod
    def change_password(cls, user_id, old_password, new_password):
        """Change user password"""
        try:
            conn, cursor = get_db()
            
            # Verify old password
            cursor.execute("SELECT password, salt FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                raise ValueError("User not found")
            
            db_password, salt = user_data
            if cls.hash_password(old_password, salt) != db_password:
                raise ValueError("Invalid old password")
            
            # Hash new password
            new_salt = cls.generate_salt()
            new_hashed_password = cls.hash_password(new_password, new_salt)
            
            # Update password
            cursor.execute("""
                UPDATE users SET password = %s, salt = %s WHERE id = %s
            """, (new_hashed_password, new_salt, user_id))
            
            conn.commit()
            cursor.close()
            
            cls.log_action(user_id, "Password changed", {})
            logging.info(f"Password changed successfully for user ID: {user_id}")
            
        except Exception as e:
            logging.error(f"Error changing password: {e}")
            raise
    
    @classmethod
    def delete_user(cls, user_id):
        """Delete user (soft delete by setting is_active to False)"""
        try:
            conn, cursor = get_db()
            cursor.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            
            cls.log_action(user_id, "User deleted", {})
            logging.info(f"User deleted successfully: ID {user_id}")
            
        except Exception as e:
            logging.error(f"Error deleting user: {e}")
            raise
    
    @classmethod
    def log_action(cls, user_id, action, details):
        """Log user actions for audit trail"""
        try:
            conn, cursor = get_db()
            cursor.execute("""
                INSERT INTO audit_logs (user_id, action, new_values, created_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, action, str(details), datetime.now()))
            conn.commit()
            cursor.close()
        except Exception as e:
            logging.error(f"Error logging action: {e}")
