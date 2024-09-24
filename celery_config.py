import os
import ssl
from celery import Celery


celery_app = Celery(
    "pubsub_listener",
    broker=os.getenv("CELERY_REDIS_URL"),
    backend=os.getenv("CELERY_REDIS_URL"),
)

celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
broker_connection_retry_on_startup = True


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

from jobs import payment_jobs
