import os

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from service.weather import get_weather, load_cities

app = FastAPI(title="Weather API")

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
