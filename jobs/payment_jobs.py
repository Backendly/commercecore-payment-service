from rq import Queue
from db.session import redis_instance
from services.stripe_config import stripe
from fastapi import HTTPException
import os
import json
import math
from rq import Queue
import logging


async def recieve_orders(*args, **kwargs):
    """Recieves orders from the payment_status channel"""
    client = redis_instance()
    pubsub = client.subscribe("payment_order_created")
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
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
                        developer_id: developer_id,
                        app_id: app_id,
                        user_id: user_id,
                    },
                )
            except stripe.error.StripeError as e:
                raise HTTPException(status_code=400, detail=f"{e}")
