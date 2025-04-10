from fastapi.testclient import TestClient
from src.main import app
import json

client = TestClient(app)

def test_fan_in_multi():
    java_code = """
        public class MultiMethod {
            public void methodOne() {
                common();
            }

            public void methodTwo() {
                common();
            }

            public void common() {
                System.out.println("Common");
            }
        }
    """
    files = {
        "file": ("MultiMethod.java", java_code)
    }
    data = {
        "function_names": json.dumps(["common", "methodOne"])
    }

    response = client.post("/metrics/fan-in-multi", data=data, files=files)

    assert response.status_code == 200
    result = response.json()
    assert "results" in result
    assert result["results"]["common"] == 2
    assert result["results"]["methodOne"] == 0
