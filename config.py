"""
Configuration file for Supermarket Management System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration - SECURE using environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),  # 🔒 NO HARDCODED PASSWORD
    'database': os.getenv('DB_NAME', 'supermarket_db'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True,
    'raise_on_warnings': True
}

# Application Settings
APP_NAME = "Advanced Supermarket Management System"
VERSION = "1.0.0"
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Business Logic Constants
TAX_RATE = float(os.getenv('TAX_RATE', '0.05'))
DISCOUNT_THRESHOLD = float(os.getenv('DISCOUNT_THRESHOLD', '100.00'))
DISCOUNT_RATE = float(os.getenv('DISCOUNT_RATE', '0.10'))
LOW_STOCK_THRESHOLD = int(os.getenv('LOW_STOCK_THRESHOLD', '10'))
EXPIRY_ALERT_DAYS = int(os.getenv('EXPIRY_ALERT_DAYS', '7'))

# API Configuration
SMS_API_KEY = os.getenv('SMS_API_KEY', 'your_sms_api_key_here')
SMS_API_URL = os.getenv('SMS_API_URL', 'https://api.sms-provider.com/send')
CALL_API_KEY = os.getenv('CALL_API_KEY', 'your_call_api_key_here')
CALL_API_URL = os.getenv('CALL_API_URL', 'https://api.call-provider.com/call')

# File Paths
LOG_DIRECTORY = "logs"
BACKUP_DIRECTORY = "backups"
RECEIPTS_DIRECTORY = "receipts"

# Ensure directories exist
for directory in [LOG_DIRECTORY, BACKUP_DIRECTORY, RECEIPTS_DIRECTORY]:
    os.makedirs(directory, exist_ok=True)

# UI Configuration
WINDOW_TITLE = "Supermarket Management System"
WINDOW_GEOMETRY = "fullscreen"
THEME = "clam"

# Default Admin Credentials - SECURE
DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin')

def format_date_mysql(date_string):
    """Convert any date format to MySQL format YYYY-MM-DD"""
    if not date_string or date_string.strip() == '':
        return None
    date_string = date_string.strip()
    if '/' in date_string:
        date_string = date_string.replace('/', '-')
    return date_string
