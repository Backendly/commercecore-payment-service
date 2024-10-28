#!/usr/bin/env python3

from db.session import redis_instance
from services.stripe_config import stripe
from fastapi import HTTPException
import json
import logging
from celery_config import celery_app
from models.payment_method_model import PaymentMethod, ConnectedAccount
from sqlalchemy.exc import SQLAlchemyError
from jobs.payment_jobs import process_order
from datetime import datetime


# Redis Listener to run separately (e.g., in redis_listener.py)
def recieve_orders():
    """Standalone Redis Pub/Sub listener that triggers Celery tasks."""
    client = redis_instance()
    pubsub = client.subscribe("payment_order_created")
    print("Listening to payment_order_created channel...")
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                print(f"Recieved a message at {datetime.today()}")
                process_order.delay(data)  # Submit task to Celery
    except Exception as e:
        logging.error(f"Error receiving orders: {e}")
        raise HTTPException(status_code=400, detail=str(e))


recieve_orders()
