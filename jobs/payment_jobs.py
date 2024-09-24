from db.session import redis_instance
from services.stripe_config import stripe
from fastapi import HTTPException
import json
import logging
from celery_config import celery_app


processed_orders = set()  # Keep track of processed order IDs


@celery_app.task(bind=True)
def receive_orders(self):
    """Receives orders from the payment_status channel (synchronously)"""
    client = redis_instance()
    pubsub = client.subscribe("payment_order_created")
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                order_id = data.get("order_id")

                if order_id not in processed_orders:
                    processed_orders.add(order_id)  # Mark as processed
                    process_order.delay(data)  # Enqueue the processing task
                else:
                    logging.info(f"Order {order_id} has already been processed.")
    except Exception as e:
        logging.error(f"Error in receive_orders: {str(e)}")
        raise HTTPException(status_code=400, detail=f"{e}")


@celery_app.task(bind=True)
def process_order(self, data):
    """Processes the order"""
    order_id = data.get("order_id")
    amount = data.get("total")
    user_id = data.get("user_id")
    developer_id = data.get("developer_id")
    app_id = data.get("app_id")
    amount = round(float(amount) * 100)
    try:
        stripe.PaymentIntent.create(
            stripe_account="acct_1Q1uwPFKeQfUzMzl",
            amount=amount,
            currency="usd",
            metadata={
                "order_id": order_id,
                "developer_id": developer_id,
                "app_id": app_id,
                "user_id": user_id,
            },
        )
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {str(e)}")
        self.retry(exc=e, countdown=60)
