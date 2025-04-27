# Test Coverage Metrics Service — Testing For New Response Format

---

## How to Run the Test Coverage Service

### 1. Navigate to the Test Coverage Service Directory

```bash
cd ser516-group-26/app/backend/python-backend/test_coverage/src/

python3 -m venv venv
source venv/bin/activate # On macOS
venv\Scripts\activate # On Windows

pip install -r ../requirements.txt

# To test the Docker Image:
cd ..
docker build -t test-coverage-service .
docker run -p 8004:8004 test-coverage-service

# To test the API locally:
uvicorn main:app --reload --host 0.0.0.0 --port 8001

---

## Endpoint to Test (with POSTMAN or Curl)
GET /metrics/test-coverage
