import zipfile
import io
import json
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_fan_in_scoped():
    # Create two .java files and zip them in memory
    java1 = """
        public class A {
            public void callMe() {
                target();
            }
            public void target() {}
        }
    """
    java2 = """
        public class B {
            public void other() {
                target();
            }
        }
    """

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("A.java", java1)
        zf.writestr("B.java", java2)
    zip_buffer.seek(0)

    files = {
        "folder": ("sample.zip", zip_buffer.read(), "application/zip")
    }
    data = {
        "scope": json.dumps({
            "selected_files": ["A.java", "B.java"],
            "function_name": "target"
        })
    }

    response = client.post("/metrics/fan-in-scoped", files=files, data=data)
    assert response.status_code == 200
    result = response.json()
    assert result["function_name"] == "target"
    assert result["total_fan_in"] == 2
