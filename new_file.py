from db.session import redis_instance
from rq import Queue
from redis_db.redis_db import CustomRedis
import redis
import json

client = redis_instance()
client = redis.Redis(
    username="default",
    password="ExU70nVyY3tt22vS8Xx0f3kN6BTWgUqu",
    host="redis-12090.c275.us-east-1-4.ec2.redns.redis-cloud.com",
    port=12090,
)
pubsub = client.pubsub()
message = {
    "message": "Hello, World",
    "status": "success",
    "status_code": 200,
    "account_id": "acct_1JbLbJGzH7J1H6qZ",
}
client.publish("crazy", json.dumps(message))
