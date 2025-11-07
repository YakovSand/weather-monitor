import requests
import gzip
import json
import os
from typing import Optional


API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


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
