import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
TEST_DIR = os.path.dirname(__file__)

def test_fan_out():
    with open(os.path.join(TEST_DIR, "Example.java"), "rb") as f:
        files = {"file": ("Example.java", f)}
        data = {"function_name": "greet"}
        response = requests.post(f"{BASE_URL}/metrics/fan-out", data=data, files=files)
        result = response.json()
        print("**** fan-out:", result)
        assert response.status_code == 200
        assert result["function_name"] == "greet"
        assert result["fan_out"] == 2

def test_fan_out_multi():
    with open(os.path.join(TEST_DIR, "Example.java"), "rb") as f:
        files = {"file": ("Example.java", f)}
        data = {"function_names": json.dumps(["greet", "hello"])}
        response = requests.post(f"{BASE_URL}/metrics/fan-out-multi", data=data, files=files)
        result = response.json()
        print("**** fan-out-multi:", result)
        assert response.status_code == 200 
        assert result["results"]["greet"] == 2 
        assert result["results"]["hello"] == 0

def test_fan_out_scoped():
    with open(os.path.join(TEST_DIR, "test_project.zip"), "rb") as f:
        files = {"folder": ("test_project.zip", f)}
        scope = {
            "selected_files": ["A.java", "B.java"],
            "function_name": "alpha"
        }
        data = {"scope": json.dumps(scope)}
        response = requests.post(f"{BASE_URL}/metrics/fan-out-scoped", data=data, files=files)
        result = response.json() 
        print("**** fan-out-scoped:", result)
        assert response.status_code == 200 
        assert result["function_name"] == "alpha"
        assert result["total_fan_out"] == 4 
        assert result["per_file_results"]["A.java"] == 2
        assert result["per_file_results"]["B.java"] == 2

def test_fan_out_scoped_multi():
    with open(os.path.join(TEST_DIR, "test_project.zip"), "rb") as f:
        files = {"folder": ("test_project.zip", f)}
        scope = {
            "selected_files": ["A.java", "B.java"],
            "function_names": ["alpha", "beta"]
        }
        data = {"scope": json.dumps(scope)}
        response = requests.post(f"{BASE_URL}/metrics/fan-out-scoped-multi", data=data, files=files)
        result = response.json()
        print("**** fan-out-scoped-multi:", result)
        assert response.status_code == 200
        assert result["results"]["alpha"]["total_fan_out"] == 4
        assert result["results"]["beta"]["total_fan_out"] == 0 

if __name__ == "__main__":
    print("*** Running Fan-out Metric Tests via Python... ***")
    test_fan_out()
    test_fan_out_multi()
    test_fan_out_scoped()
    test_fan_out_scoped_multi()
    print("**** All tests passed successfully. ****")
