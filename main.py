import os

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from connections import connect_rabbitmq, connect_elasticsearch
from service.weather import get_weather, load_cities, send_weather_to_queue

app = FastAPI(title="Weather API")

# Read flag from environment
ENABLE_DEPENDENCIES = os.getenv("ENABLE_DEPENDENCIES", "true").lower() == "true"

# Connect on startup
@app.on_event("startup")
def startup_event():
    if ENABLE_DEPENDENCIES:
        app.state.rabbitmq_connection = connect_rabbitmq()
        app.state.elasticsearch = connect_elasticsearch()
        print("Dependencies initialized!")
        # Scheduler: sample every hour
        scheduler = BackgroundScheduler()
        # Example: fetch weather for London every 2 minutes TODO: change to every hour
        scheduler.add_job(lambda: send_weather_to_queue("London"), 'interval', minutes=2)
        scheduler.start()
    else:
        print("Dependencies initialization skipped!")

# Mount static files just if the directory exists and skip for the tests
static_dir = "pages"
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"Warning: static directory '{static_dir}' not found. Skipping mount.")

# Folder with HTML templates
pages = Jinja2Templates(directory="pages")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, city: str = Query(default=None)):
    """
    A primary form to enter a city name and display the weather info.
    :param request:
    :param city:
    :return: HTML page with weather info.
    """
    weather_info = None
    error = None

    if city:
        try:
            weather_info = get_weather(city)
        except Exception as e:
            error = str(e)

    return pages.TemplateResponse(
        "index.html",
        {"request": request, "weather": weather_info, "error": error, "city": city or ""}
    )


@app.get("/weather")
def weather_api(city: str):
    """
    API endpoint: /weather?city=London
    Returns current weather data in JSON format for the specified city.
    """
    print("City received:", city)
    data = get_weather(city)
    print("Data fetched:", data)
    return data


@app.get("/city-list", response_class=HTMLResponse)
def city_list(request: Request):
    """
    Used for dynamically loading a large list of cities.
    [limit] cities are loaded from the service layer.
    :param request:
    :return:  HTML page with city list.
    """
    cities = load_cities(limit=50000)  # load top 50000 cities dynamically
    return pages.TemplateResponse("city_list.html", {"request": request, "cities": cities})
