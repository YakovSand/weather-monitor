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


# ----------------------
# Elasticsearch Connection
# ----------------------
def connect_elasticsearch(retries=100, initial_delay=20, max_delay=60):
    elastic_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
    delay = initial_delay
    for attempt in range(1, retries + 1):
        try:
            es = Elasticsearch([elastic_url])
            if es.ping():
                print("Connected to Elasticsearch")
                logger.info("Connected to Elasticsearch")
                return es
            else:
                print(f"Attempt {attempt}: Elasticsearch not responding")
                logger.info(f"Attempt {attempt}: Elasticsearch not responding")
        except Exception as e:
            print(f"Elasticsearch connection failed (attempt {attempt}/{retries}): {e}")
            logger.error(f"Elasticsearch connection failed (attempt {attempt}/{retries}): {e}")

        if attempt < retries:
            print(f"Waiting {delay} seconds before retrying...")
            logger.error(f"Waiting {delay} seconds before retrying...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)  # exponential backoff, capped at max_delay

    raise Exception("Could not connect to Elasticsearch after multiple retries")
