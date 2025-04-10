import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_fan_in_endpoint_success():
    with TestClient(app) as client:
    # Simulated Java source code with two external calls to "sayHi"
        java_code = """
            public class HelloWorld {
                public void test() {
                    sayHi();
                    sayHi();
                }

                public void sayHi() {
                    System.out.println("Hello");
                }
            }
        """
        # Simulate form data and file upload
        files = {
            "file": ("HelloWorld.java", java_code)
        }
        data = {
            "function_name": "sayHi"
        }

        # Send POST request to the /metrics/fan-in endpoint
        response = client.post("/metrics/fan-in", data=data, files=files)

        # Assertions
        assert response.status_code == 200
        json_data = response.json()
        assert "function_name" in json_data
        assert "fan_in" in json_data
        assert json_data["function_name"] == "sayHi"
        assert isinstance(json_data["fan_in"], int)
        assert json_data["fan_in"] == 2

def test_fan_in_endpoint_wrong_file_type():
    with TestClient(app) as client:
        files = {
            "file": ("HelloWorld.txt", "just some text")
        }
        data = {
            "function_name": "sayHi"
        }

        response = client.post("/metrics/fan-in", data=data, files=files)
        assert response.status_code == 400
        assert response.json()["detail"] == "Only Java files are supported"

def test_fan_in_endpoint_missing_function_name():
    with TestClient(app) as client:
        java_code = """
            public class HelloWorld {
                public void test() {
                    sayHi();
                }

                public void sayHi() {
                    System.out.println("Hello");
                }
            }
        """
        files = {
            "file": ("HelloWorld.java", java_code)
        }

        response = client.post("/metrics/fan-in", files=files)
        assert response.status_code == 422  # Unprocessable Entity due to missing 'function_name'
