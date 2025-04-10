import requests

BASE_URL = "http://127.0.0.1:8002"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "Fan-out Metrics Service" in data.get("message", "")

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "javaparser" in data