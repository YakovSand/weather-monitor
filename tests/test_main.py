from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test the /weather endpoint
def test_get_weather():
    city = "London"
    response = client.get("/weather", params={"city": city})
    assert response.status_code == 200

    data = response.json()
    assert data["city"] == city
    assert "temperature" in data
    assert "humidity" in data
    assert "description" in data
