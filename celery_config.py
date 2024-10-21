from dotenv import load_dotenv
import pymysql
import os
import ssl
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pymysql.install_as_MySQLdb()
load_dotenv()

DATABASE_URL = os.getenv("T_DATABASE", "DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
