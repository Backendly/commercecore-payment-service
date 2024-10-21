from db.session import redis_instance
from services.stripe_config import stripe
from fastapi import HTTPException
import json
import logging
from celery_config import celery_app
from celery_config import LocalSession
from models.payment_method_model import PaymentMethod
from models.payment_method_model import ConnectedAccount


@celery_app.task(bind=True)
def receive_orders(self):
    """Receives orders from the payment_status channel (synchronously)"""
    client = redis_instance()
    pubsub = client.subscribe("payment_order_created")
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                process_order.delay(data)
    except Exception as e:
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
        session = LocalSession()
        account_id = (
            session.query(ConnectedAccount)
            .filter_by(developer_id=developer_id)
            .first()
            .account_id
        )
        payment_intent = stripe.PaymentIntent.create(
            stripe_account=account_id,
            amount=amount,
            currency="usd",
            metadata={
                "order_id": order_id,
                "developer_id": developer_id,
                "app_id": app_id,
                "user_id": user_id,
            },
        )
        confirm_payment.delay(payment_intent)
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {str(e)}")
        self.retry(exc=e, countdown=60)
    finally:
        session.close()


@celery_app.task(bind=True)
def confirm_payment(self, data):
    """Confirms the payment"""
    try:
        developer_id = data.get("metadata").get("developer_id")
        user_id = data.get("metadata").get("user_id")
        app_id = data.get("metadata").get("app_id")
        session = LocalSession()
        payment_method_id = (
            session.query(PaymentMethod)
            .filter_by(
                developer_id=developer_id,
                app_id=app_id,
                user_id=user_id,
                preferred=True,
            )
            .first()
            .payment_method_id
        )
        payment_intent = stripe.PaymentIntent.confirm(
            data.get("id"), payment_method=payment_method_id
        )
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {str(e)}")
        self.retry(exc=e, countdown=60)

    finally:
        session.close()
