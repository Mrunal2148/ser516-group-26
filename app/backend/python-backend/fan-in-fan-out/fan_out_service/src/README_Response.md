# Fan-Out Metrics Service — Testing For New Response Format

---

## How to Run the Fan-Out Service

### 1. Navigate to the Fan-Out Service Directory

```bash
cd ser516-group-26/app/backend/python-backend/fan-in-fan-out/fan_out_service/src/

python3 -m venv venv
source venv/bin/activate # On macOS
venv\Scripts\activate # On Windows

pip install -r ../requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8002

---

## Endpoint to Test (with POSTMAN or Curl)
POST /metrics/fan-out-scoped-multi
POST /metrics/fan-out
POST /metrics/fan-out/multi