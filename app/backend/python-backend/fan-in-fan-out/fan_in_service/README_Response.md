# Fan-In Metrics Service — Testing For New Response Format

---

## How to Run the Fan-In Service

### 1. Navigate to the Fan-In Service Directory

```bash
cd ser516-group-26/app/backend/python-backend/fan-in-fan-out/fan_in_service/src/

python3 -m venv venv
source venv/bin/activate # On macOS
venv\Scripts\activate # On Windows

pip install -r ../requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8001

---

## Endpoint to Test (with POSTMAN or Curl)
POST /metrics/fan-in-scoped-multi
POST /metrics/fan-in
POST /metrics/fan-in/multi