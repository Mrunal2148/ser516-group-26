# Project Metrics Calculator

The **Project Metrics Calculator** is a web-based application designed to help developers analyze and improve their code quality by providing essential software quality metrics. It features a **React frontend** with **Java** and **Python backends**, containerized using **Docker** and orchestrated through **Docker Compose**.

## Features
- **Fog Index Metric:** Measures the readability of code comments.
- **Defects Removed Metric:** Evaluates how many defects have been fixed in the codebase.
- **Code Comment Coverage:** Calculates the percentage of commented code to ensure maintainability.

## Tech Stack
- **Frontend:** React.js
- **Backends:**  
  - Java (for core metric computations)  
  - Python (for repository analysis and comment coverage metrics)  
- **Containerization:** Docker & Docker Compose
- **Version Control:** GitHub

---

## Getting Started
### Prerequisites
- Docker & Docker Compose installed.
- A valid GitHub token for repository analysis.

### Environment Variables
GITHUB Token
To generate a GitHub personal access token (PAT) for developers, follow these steps:

Step 1: Log into GitHub
  Go to GitHub and log into your account.
Step 2: Navigate to Developer Settings
  Click on your profile picture (top-right corner).
  Select "Settings" from the dropdown.
  Scroll down and find "Developer settings" (on the left sidebar).
  Click "Personal access tokens", then choose "Tokens (classic)" (or "Fine-grained tokens" if you need more control).
Step 3: Generate a New Token
  Click "Generate new token", then choose:
  Classic token (widely used and easier to configure)
  Fine-grained token (for more specific permissions)
  Give your token a note/name for identification.
  Set Expiration (recommended for security).
Select Permissions:
![image](https://github.com/user-attachments/assets/cc2e48b4-d508-41cf-8617-8328aa794b99)
  For repository access, check repo.
  For GitHub Actions, check workflow.
  For Git operations (push/pull), check write:packages, read:packages.
  For Full access, check all necessary scopes.
  Click "Generate token".
Step 4: Copy and Store the Token
  Copy the token immediately and store it securely (e.g., in a password manager).

### Installation & Running
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mrunal2148/ser516-group-java-2.git
   cd app
   touch .env
   echo GITHUB_TOKEN=your_github_token_here >> .env
   ```

2. **Start the application:**

## ⚙️ How to Run

### 🐳 Option 1: Run with Docker (Recommended)

> Make sure Docker is installed and running.

```bash
# Clone the repo
git clone https://github.com/your-username/metrics-calculator.git
cd metrics-calculator

# Build all services
docker build -t app-frontend ./app/frontend
docker build -t app-java-backend ./app/backend
docker build -t app-python-backend ./app/backend/python-backend
docker build -t app-code-comment-coverage-backend ./app/backend/python-backend/code-comment
docker build -t app-fan-in-fan-out-api ./app/backend/python-backend/fan-in-fan-out/api_gateway -f ./app/backend/python-backend/fan-in-fan-out/api_gateway/src/Dockerfile
docker build -t app-fan-in-service ./app/backend/python-backend/fan-in-fan-out/fan_in_service -f ./app/backend/python-backend/fan-in-fan-out/fan_in_service/src/Dockerfile
docker build -t app-fan-out-service ./app/backend/python-backend/fan-in-fan-out/fan_out_service -f ./app/backend/python-backend/fan-in-fan-out/fan_out_service/src/Dockerfile
docker build -t app-github-service ./app/backend/python-backend/fan-in-fan-out/GitHub_service -f ./app/backend/python-backend/fan-in-fan-out/GitHub_service/src/Dockerfile

# Run the containers (you can script this or use docker-compose)
docker run -d -p 6000:6000 --name app-code-comment-coverage-backend-1 ser516/app-code-comment-coverage-backend:latest
docker run -d -p 5000:5000 --name app-python-backend-1 ser516/app-python-backend:latest
docker run -d -p 8080:8080 --name app-java-backend-1 ser516/app-java-backend:latest
docker run -d -p 3000:3000 --name app-frontend-1 ser516/app-frontend:latest
docker run -d -p 7000:7000 --name app-github-service-1 ser516/app-github-service:latest
docker run -d -p 7100:7100 --name app-fan-in-service-1 ser516/app-fan-in-service:latest
docker run -d -p 7200:7200 --name app-fan-out-service-1 ser516/app-fan-out-service:latest
docker run -d -p 7300:7300 --name app-fan-in-fan-out-api-1 ser516/app-fan-in-fan-out-api:latest



3. **Access the application:**
   - Frontend: [http://localhost:3000](http://localhost:3000)  
   - Java Backend: [http://localhost:8080](http://localhost:8080)  
   - Python Backend: [http://localhost:5005](http://localhost:5005)  
```

## Project Structure
```
project-metrics-calculator/
├── frontend/           # React application
├── backend/
│   ├── Dockerfile      # Java backend Docker setup
│   └── python-backend/
│       ├── Dockerfile  # Python backend Docker setup
│       └── ...         # Python code for metrics
├── docker-compose.yml  # Docker orchestration file
└── .env                # Environment variables
```

## Team
- **Kaumudi Gulbarga** - Developer  
- **Mrunal Kapure** - Developer  
- **Parth Patel** - Developer  
- **Shreya Prakash** - Developer


# 📊 Metrics Calculator

**Metrics Calculator** is a modular web application designed to compute and analyze code and project metrics, providing insights across multiple services. It leverages a microservice architecture built using Python, Java, and React, and uses GitHub Actions for CI/CD.

---

## 🚀 Features

- Multi-container microservices architecture
- Code comment and coverage analysis
- GitHub repository metrics processing
- Fan-in/fan-out service-based data flow
- Interactive frontend built with React
- CI/CD with Docker and GitHub Actions

---

## 🛠️ Tech Stack

- **Frontend:** React
- **Backend:** Python (Flask), Java (Spring Boot)
- **Containerization:** Docker
- **CI/CD:** GitHub Actions
- **Testing:** PyTest, Unittest, Jest

---

## 📁 Project Structure

metrics-calculator/ │ ├── app/ │ ├── frontend/ # React frontend │ └── backend/ │ ├── python-backend/ │ │ ├── code-comment/ # Code comment coverage service │ │ └── fan-in-fan-out/ │ │ ├── api_gateway/ # API Gateway │ │ ├── fan_in_service/ # Fan-in service │ │ ├── fan_out_service/ # Fan-out service │ │ └── GitHub_service/ # GitHub metrics processor │ └── java-backend/ # Java backend module │ ├── .github/workflows/ │ └── ci-cd.yml # CI/CD GitHub Actions workflow


---

## ⚙️ GitHub Actions: CI/CD Pipeline

This app uses GitHub Actions for automating the build, test, and deploy process.

### 🔁 Triggered On

- Push to `Period-3` and `dev` branches
- Pull requests to `Period-3` and `dev`
- Manual dispatch (`workflow_dispatch`)

### 🔨 Build Job

- Checks out the repository
- Sets up Docker Buildx
- Builds and tags Docker images:
  - `app-frontend`
  - `app-java-backend`
  - `app-python-backend`
  - `app-code-comment-coverage-backend`
  - `app-fan-in-fan-out-api`
  - `app-fan-in-service`
  - `app-fan-out-service`
  - `app-github-service`
- Logs into Docker Hub using secrets
- Pushes all tagged images to Docker Hub

### ✅ Test Job

- Runs after the `build` job
- Installs Python 3.10
- Installs dependencies from `requirements.txt`
- Runs:
  - Unittest for `code-comment` module
  - PyTest for `test_app.py`
  - Frontend tests using Jest

---

## 🐳 Docker Images (Pushed to Docker Hub)

- `mkapure/app-frontend:latest`
- `mkapure/app-java-backend:latest`
- `mkapure/app-python-backend:latest`
- `mkapure/app-code-comment-coverage-backend:latest`
- `mkapure/app-fan-in-fan-out-api:latest`
- `mkapure/app-fan-in-service:latest`
- `mkapure/app-fan-out-service:latest`
- `mkapure/app-github-service:latest`

---

## 📦 Requirements

- Docker
- Node.js & npm (for frontend)
- Python 3.10+
- Java 17+ (for Java backend)

---

## 🧪 Running Tests Locally

```bash
# Frontend
cd app/frontend
npm install
npm test

# Python backend
cd app/backend/python-backend
pip install -r requirements.txt
pytest

# Code comment module
cd app/backend/python-backend/code-comment
PYTHONPATH=. python -m unittest discover -s tests
```



