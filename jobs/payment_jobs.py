from db.session import redis_instance
from services.stripe_config import stripe
from fastapi import HTTPException
import json
import logging
from celery_config import celery_app
from celery_config import LocalSession
from models.payment_method_model import PaymentMethod
from models.payment_method_model import ConnectedAccount
import pymysql

pymysql.install_as_MySQLdb()


# @celery_app.task(bind=True)
# def recieve_orders(self):
#     """Standalone Redis Pub/Sub listener that triggers Celery tasks."""
#     client = redis_instance()
#     pubsub = client.subscribe("payment_order_created")
#     logging.info("Listening to payment_order_created channel...")
#     try:
#         for message in pubsub.listen():
#             if message["type"] == "message":
#                 data = json.loads(message["data"])
#                 process_order.delay(data)  # Submit task to Celery
#     except Exception as e:
#         logging.error(f"Error receiving orders: {e}")
#         raise HTTPException(status_code=400, detail=str(e))


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
        connected_account = (
            session.query(ConnectedAccount).filter_by(developer_id=developer_id).first()
        )

        account_id = connected_account.account_id
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
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
        )

        logging.info("Proceeding to Get Confirmation of Payment...")
        confirm_payment.delay(payment_intent, account_id)
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=5)
    finally:
        session.close()


@celery_app.task(bind=True, default_retry_delay=60, max_retries=5)
def confirm_payment(self, data, account_id):
    """Confirms the payment"""
    logging.info("Starting Payment Confirmation...")
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
            data.get("id"), payment_method=payment_method_id, stripe_account=account_id
        )
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {str(e)}")
        self.retry(exc=e, countdown=1200)

    finally:
        session.close()
