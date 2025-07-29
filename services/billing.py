"""
Billing service for transaction calculations
Copyright (c) 2024 [Your Name]. All rights reserved.
"""
from config import TAX_RATE, DISCOUNT_THRESHOLD, DISCOUNT_RATE

class BillingService:
    @staticmethod
    def calculate_total(cart_items):
        """Calculate subtotal, discount, tax, and total amounts"""
        subtotal = sum(item['quantity'] * item['unit_price'] for item in cart_items)
        
        # Apply discount if eligible
        discount_amount = 0.0
        if subtotal >= DISCOUNT_THRESHOLD:
            discount_amount = subtotal * DISCOUNT_RATE
        
        # Calculate tax on discounted amount
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * TAX_RATE
        
        # Final total
        total_amount = subtotal - discount_amount + tax_amount
        
        return {
            'subtotal': round(subtotal, 2),
            'discount_amount': round(discount_amount, 2),
            'tax_amount': round(tax_amount, 2),
            'total_amount': round(total_amount, 2)
        }
