import zipfile
import io
import json
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_fan_in_scoped_multi():
    java1 = """
        public class A {
            public void alpha() {
                beta();
                gamma();
            }
            public void beta() {}
        }
    """
    java2 = """
        public class B {
            public void gamma() {
                System.out.println("gamma");
            }
        }
    """

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("A.java", java1)
        zf.writestr("B.java", java2)
    zip_buffer.seek(0)

    files = {
        "folder": ("multi.zip", zip_buffer.read(), "application/zip")
    }
    data = {
        "scope": json.dumps({
            "selected_files": ["A.java", "B.java"],
            "function_names": ["beta", "gamma"]
        })
    }

    response = client.post("/metrics/fan-in-scoped-multi", files=files, data=data)
    assert response.status_code == 200
    result = response.json()["results"]
    assert result["beta"]["total_fan_in"] == 1
    assert result["gamma"]["total_fan_in"] == 1
