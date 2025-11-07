# Weather Monitor

A simple web application to display weather data for world cities.

---

## Features

- Fetch current weather for a city using OpenWeatherMap API.
- Dynamic list of cities with search functionality.
---

## Prerequisites

- Python 3.10+  
- pip  
- Docker installed (optional, for containerization (E2E pipeline with RabbitMQ, Elasticsearch, Grafana))

---

## Setup

1. Clone the repository
2. Create virtual environment:
    python -m venv .venv
3. Activate virtual environment:
    - On Windows: `.venv\Scripts\activate`
    - On macOS/Linux: `source .venv/bin/activate`
4. Install dependencies:
    pip install -r requirements.txt
5. Set your OpenWeatherMap API key as an environment variable:
    - On Windows: `set OPENWEATHER_API_KEY=your_api_key`
    - On macOS/Linux: `export OPENWEATHER_API_KEY=your_api_key`

---
## Run the Application
1. Start the FastAPI server:
    uvicorn main:app --reload
2. Open your browser and navigate to `http://localhost:8000/` to view the application home page.

---
## Docker Deployment (Optional)
1. Build the Docker image:
    docker build -t fastapi-weather-monitor:latest .
2. Run the Docker container:
    docker run --rm -p 8000:8000 fastapi-weather-monitor:latest
3. Access the application at `http://localhost:8000/`.

---

