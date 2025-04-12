# Project Metrics Calculator

The **Project Metrics Calculator** is a web-based application designed to help developers analyze and improve their code quality by providing essential software quality metrics. It features a **React frontend** with **Java** and **Python backends**, containerized using **Docker** and orchestrated through **Docker Compose**.

## Features
- **Fog Index Metric:** Measures the readability of code comments.
- **Defects Removed Metric:** Evaluates how many defects have been fixed in the codebase.
- **Code Comment Coverage:** Calculates the percentage of commented code to ensure maintainability.
- **Test Churn:** Calculates added, deleted and updated metrics.
- **Fan In / Fan Out:** Calculates fan-in fan-out against metrics.

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
   ```bash
   docker pull mkapure/app-code-comment-coverage-backend:latest
   docker pull mkapure/app-python-backend:latest
   docker pull mkapure/app-java-backend:latest
   docker pull mkapure/app-frontend:latest
   docker pull mkapure/app-github-service:latest
   docker pull mkapure/app-fan-in-service:latest
   docker pull mkapure/app-fan-out-service:latest
   docker pull mkapure/app-fan-in-fan-out-api:latest

   docker run -d -p 6000:6000 --name app-code-comment-coverage-backend-1 mkapure/app-code-comment-coverage-backend:latest
   docker run -d -p 5000:5000 --name app-python-backend-1 mkapure/app-python-backend:latest
   docker run -d -p 8080:8080 --name app-java-backend-1 mkapure/app-java-backend:latest
   docker run -d -p 3000:3000 --name app-frontend-1 mkapure/app-frontend:latest
   docker run -d -p 7000:7000 --name app-github-service-1 mkapure/app-github-service:latest
   docker run -d -p 7100:7100 --name app-fan-in-service-1 mkapure/app-fan-in-service:latest
   docker run -d -p 7200:7200 --name app-fan-out-service-1 mkapure/app-fan-out-service:latest
   docker run -d -p 7300:7300 --name app-fan-in-fan-out-api-1 mkapure/app-fan-in-fan-out-api:latest
   ```
3. **Access the application:**
   - App: [http://localhost:3000](http://localhost:3000)  

---

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
- **Ripudaman Singh** - Developer
- **Sahithi Karangala** - Developer
- **Aditya Kumar** - Developer
- **Siddhnat Shah** - Developer


