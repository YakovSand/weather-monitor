import pika
import requests
import gzip
import json
import os
from typing import Optional

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "weather"

def get_weather(city: str):
    """
    Fetch weather data from OpenWeatherMap API.
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Failed to get weather for '{city}'. {response.text}")

    data = response.json()
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "icon": data["weather"][0]["icon"]
    }


def load_cities(limit: Optional[int] = None):
    url = "http://bulk.openweathermap.org/sample/city.list.json.gz"
    response = requests.get(url)

    with open("data/city.list.json.gz", "wb") as f:
        f.write(response.content)

    print("Downloaded city.list.json.gz")

    with gzip.open("data/city.list.json.gz", "rt", encoding="utf-8") as f:
        all_cities = json.load(f)

    # Keep only city name and country (optionally limited)
    if limit is not None:
        filtered = [{"name": c["name"], "country": c["country"]} for c in all_cities[:limit]]
        print("Total cities loaded (limited):", len(filtered))
    else:
        print("Total cities loaded:", len(all_cities))
        filtered = [{"name": c["name"], "country": c["country"]} for c in all_cities]
    return filtered


# Create a global connection (or use dependency injection)
class RabbitMQClient:
    def __init__(self):
        self.params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = None
        self.channel = None

    def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self.params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def publish(self, message: dict):
        self.connect()
        self.channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()


# Global instance
rabbitmq_client = RabbitMQClient()


def send_weather_to_queue(city: str):
    try:
        data = get_weather(city)
        rabbitmq_client.publish(data)
        print(f"Weather sent to queue for {city}: {data}")
    except Exception as e:
        print(f"Error sending weather for {city}: {e}")
        # Optionally reconnect on error
        rabbitmq_client.connect()