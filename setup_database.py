"""
Automated Database Setup for Supermarket Management System
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
from datetime import datetime
import getpass

def create_database():
    print("🚀 Supermarket Management System - Database Setup")
    print("=" * 50)
    
    # Get MySQL credentials securely
    host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    user = input("MySQL Username (default: root): ").strip() or "root"
    password = getpass.getpass("MySQL Password: ")
    
    try:
        # Connect to MySQL
        print("\n📡 Connecting to MySQL...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        
        # Create database
        print("🗄️  Creating database...")
        cursor.execute("DROP DATABASE IF EXISTS supermarket_db")
        cursor.execute("CREATE DATABASE supermarket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE supermarket_db")
        
        # Create tables - your existing table creation code from database.py
        print("📋 Creating tables...")
        # Add your table creation SQL here
        
        # Create default admin user
        print("👤 Creating admin user...")
        admin_password = "admin123"
        salt = secrets.token_hex(32)
        hashed = hashlib.sha256((admin_password + salt).encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (username, password, salt, role, email) 
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin', hashed, salt, 'admin', 'admin@supermarket.com'))
        
        connection.commit()
        
        print("\n✅ Setup completed successfully!")
        print(f"🔐 Login with: admin / {admin_password}")
        print("⚠️  Change password after first login!")
        
        # Create .env file
        env_content = f"""DB_HOST={host}
DB_USER={user}
DB_PASSWORD={password}
DB_NAME=supermarket_db
DEBUG_MODE=True
TAX_RATE=0.05
DISCOUNT_THRESHOLD=100.00
DISCOUNT_RATE=0.10
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("📝 Created .env file with your credentials")
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

if __name__ == "__main__":
    create_database()
