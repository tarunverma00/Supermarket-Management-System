"""
Models package for Supermarket Management System
Contains all data models and database operations
"""

# Import all models for easy access
from .user import User
from .employee import Employee
from .customer import Customer
from .product import Product
from .transaction import Transaction
from .supplier import Supplier

__all__ = [
    'User',
    'Employee', 
    'Customer',
    'Product',
    'Transaction',
    'Supplier'
]
