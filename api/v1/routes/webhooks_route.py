from fastapi import APIRouter, Request
import stripe.webhook
import stripe.webhook
from services.stripe_config import stripe
from fastapi import HTTPException
from db.session import redis_instance
import json
from rq import Queue
import os

router = APIRouter(tags=["webhooks"], prefix="/api/v1")
signing_secret = os.getenv("WEBHOOK_SECRET")


@router.post("/webhooks")
async def create_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, signing_secret)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        order_id = event["data"]["object"]["metadata"]["order_id"]
        status = event["data"]["object"]["status"]
        client = redis_instance()
        payload = {"order_id": order_id, "status": status}
        client.publish("payment_status", json.dumps(payload))

    if event["type"] == "payment_intent.created":
        order_id = event["data"]["object"]["metadata"]["order_id"]
        payload = {
            "order_id": order_id,
            "status": "created",
        }
        client = redis_instance()
        client.publish("payment_status", json.dumps(payload))

    if event["type"] == "payment_intent.payment_failed":
        order_id = event["data"]["object"]["metadata"]["order_id"]
        payload = {
            "order_id": order_id,
            "status": "failed",
        }
        client = redis_instance()
        client.publish("payment_status", json.dumps(payload))

    if event["type"] == "refund.created":
        order_id = event["data"]["object"]["metadata"]["order_id"]
        payload = {
            "order_id": order_id,
            "status": "refunded",
        }
        client = redis_instance()
        client.publish("payment_status", json.dumps(payload))
