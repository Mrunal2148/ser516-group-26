# How to Run the Project – SER516 Group 26

## 💻 Cloning the Repository

```bash
git clone https://github.com/Mrunal2148/ser516-group-26
cd ser516-group-26/
```

## 🐳 Docker (Run The Project) (Optional – For full-stack containerized deployment)

```bash
# From root of the repo (app/)
cd app/
docker-compose build --no-cache
docker-compose up
```

# For Testing Purposes

This guide explains how to set up and run each component of the project locally, for unit testing only... It includes steps for the **Unit Testing** of all microservices.

## 🐍 Backend (Python Microservices)

### 💻 Fan-In Service

```bash
cd app/backend/python-backend/fan-in-fan-out/fan_in_service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate         # macOS / Linux
venv\Scripts\activate          # Windows

# Install required dependencies
pip install -r requirements.txt

# Check if JAVA_HOME is set
echo $JAVA_HOME

# If not, set JAVA_HOME:
# macOS:
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# Windows:
# Set JAVA_HOME in Environment Variables to:
# C:\Program Files\Java\jdk-17
# Add %JAVA_HOME%\bin to the PATH variable

# Start FastAPI service (for unit testing only)
cd src
uvicorn main:app --port 8000 --reload

# Run Unit Tests
open a new terminal
cd ..
pytest tests/ -v
```

---

### 💻 Fan-Out Service

```bash
cd app/backend/python-backend/fan-in-fan-out/fan_out_service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate         # macOS / Linux
venv\Scripts\activate          # Windows

# Install required dependencies
pip install -r requirements.txt

# Check if JAVA_HOME is set
echo $JAVA_HOME

# If not, set JAVA_HOME:
# macOS:
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# Windows:
# Set JAVA_HOME in Environment Variables to:
# C:\Program Files\Java\jdk-17
# Add %JAVA_HOME%\bin to the PATH variable

# Start FastAPI service (for unit testing only)
cd src
uvicorn main:app --port 8000 --reload

# Run Unit Tests
open a new terminal
cd ..
pytest tests/ -v
```

---

### 💻 Java Backend (Defects Removed Service)

```bash
cd app/backend

# Run unit tests with Maven
mvn test
```

---

## 💻 Frontend (React App)

### Setup & Run

```bash
cd app/frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## Unit Testing – Frontend

### Code Comment Coverage

```bash
cd app/frontend
npm test -- --watchAll
```

### Fog Index Calculator

```bash
cd app/frontend
npm test -- --watchAll
```

---

#### APPRECIATION MESSAGE FROM SER516 Group 26 :)

---
