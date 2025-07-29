"""
Voice call service for customer communication
Copyright (c) 2024 [Your Name]. All rights reserved.
"""
import logging
from config import CALL_API_KEY, CALL_API_URL

class CallService:
    @staticmethod
    def make_call(phone_number, message_text, voice_type="female"):
        """Make automated voice call to customer"""
        try:
            logging.info(f"Voice call made to {phone_number}: {message_text}")
            return True  # Mock success
        except Exception as e:
            logging.error(f"Error making call: {e}")
            return False
    
    @staticmethod
    def call_customer_for_payment_reminder(phone_number, customer_name, amount_due):
        """Call customer for payment reminder"""
        message = f"Hello {customer_name}, this is a friendly reminder about your outstanding payment of ${amount_due:.2f}."
        return CallService.make_call(phone_number, message)
