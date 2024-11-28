import razorpay
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

class PaymentGateway:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )

    def create_order(self, amount: float, currency: str = "INR"):
        try:
            data = {
                "amount": int(amount * 100),  # Amount in paise
                "currency": currency,
                "payment_capture": 1
            }
            order = self.client.order.create(data=data)
            return order
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def verify_payment(self, payment_id: str, order_id: str, signature: str):
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            return True
        except Exception:
            return False