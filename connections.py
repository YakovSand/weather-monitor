import time
import os
import pika
import logging
from elasticsearch import Elasticsearch

logger = logging.getLogger("connections")

# ----------------------
# RabbitMQ Connection
# ----------------------
def connect_rabbitmq(retries=10, delay=5):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")

    for attempt in range(1, retries + 1):
        try:
            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
            )
            print("Connected to RabbitMQ")
            logger.info("Connected to RabbitMQ")
            return connection
        except Exception as e:
            print(f"RabbitMQ connection failed (attempt {attempt}/{retries}): {e}")
            logger.error(f"RabbitMQ connection failed (attempt {attempt}/{retries}): {e}")
            time.sleep(delay)
    raise Exception("Could not connect to RabbitMQ after multiple retries!")

